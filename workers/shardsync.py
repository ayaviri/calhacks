import torch
import torch.nn as nn
from torchvision.models import resnet18
import coremltools as ct

def create_sharded_model(num_shards=4):
    model = resnet18(num_classes=10)
    model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    
    shards = []
    layers = list(model.children())
    shard_size = len(layers) // num_shards
    
    for i in range(num_shards):
        start = i * shard_size
        end = (i + 1) * shard_size if i < num_shards - 1 else len(layers)
        shard = nn.Sequential(*layers[start:end])
        shards.append(shard)
    
    return shards

def load_and_sync_shards(num_shards=4):

    full_model = resnet18(num_classes=10)
    full_model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    
    layers = list(full_model.children())
    shard_size = len(layers) // num_shards
    
    for i in range(num_shards):

        mlmodel = ct.models.MLModel(f"resnet18_shard_{i}.mlmodel")
        
        pytorch_model = ct.converters.convert(mlmodel, source="coreml")
        
        start = i * shard_size
        end = (i + 1) * shard_size if i < num_shards - 1 else len(layers)
        
        for j, layer in enumerate(layers[start:end]):
            if hasattr(layer, 'weight'):
                layer.weight.data.copy_(pytorch_model[j].weight.data)
            if hasattr(layer, 'bias') and layer.bias is not None:
                layer.bias.data.copy_(pytorch_model[j].bias.data)
    
    return full_model

def save_synchronized_model(model):
    torch.save(model.state_dict(), 'resnet18_synchronized.pt')
    print("Synchronized model saved as 'resnet18_synchronized.pt'")
    
    example_input = torch.randn(1, 1, 224, 224)
    traced_model = torch.jit.trace(model, example_input)
    
    mlmodel = ct.convert(
        traced_model,
        inputs=[ct.ImageType(name="input", shape=example_input.shape, color_layout='G', channel_first=True)],
        outputs=[ct.TensorType(name="output")],
        minimum_deployment_target=ct.target.iOS16
    )
    
    mlmodel.save("resnet18_synchronized.mlmodel")
    print("Synchronized Core ML model saved as 'resnet18_synchronized.mlmodel'")

def main():
    num_shards = 4  

    synchronized_model = load_and_sync_shards(num_shards)

    save_synchronized_model(synchronized_model)

if __name__ == "__main__":
    main()