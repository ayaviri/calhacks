import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
import coremltools as ct

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

trainset = torchvision.datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=32, shuffle=True, num_workers=2)

testset = torchvision.datasets.FashionMNIST(root='./data', train=False, download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=32, shuffle=False, num_workers=2)

model = resnet18(weights=ResNet18_Weights.DEFAULT)
model.conv1 = torch.nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
model.fc = torch.nn.Linear(model.fc.in_features, 10)  
model = model.to(device)

# get_model_info: Model -> String Number
def get_model_info(model):
    model_id = model.__class__.__name__
    num_layers = len(list(model.modules()))
    return model_id, num_layers

model_id, num_layers = get_model_info(model)

print(f"Model ID: {model_id}")
print(f"Number of layers: {num_layers}")

# 1) This is the initial save to tensor
torch.save(model.state_dict(), 'fashion_mnist_resnet18.pt')
print("PyTorch model saved as 'fashion_mnist_resnet18.pt'")

dummy_input = torch.randn(1, 1, 224, 224)  

traced_script_module = torch.jit.trace(model, dummy_input)
traced_script_module.save("traced_resnet_model.pt")
print("TorchScript model saved as 'traced_resnet_model.pt'")


scale = 1 / (0.5 * 255.0)
bias = -1.0  
 