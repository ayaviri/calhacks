import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
import torch.multiprocessing as mp
from torchvision.models import resnet18
import torchvision
import torchvision.transforms as transforms

# fill in with .env file
# def setup(rank, world_size):
    # os.environ['MASTER_ADDR'] = 'localhost'
    # os.environ['MASTER_PORT'] = '12355'
    # dist.init_process_group("gloo", rank=rank, world_size=world_size)

def cleanup():
    dist.destroy_process_group()

def train(rank, world_size):
    setup(rank, world_size)

    if not torch.backends.mps.is_available():
        print(f"MPS not available on device {rank}. Using CPU instead.")
        device = torch.device("cpu")
    else:
        device = torch.device("mps")

    model = resnet18(num_classes=10)
    model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    model = model.to(device)

    model = nn.parallel.DistributedDataParallel(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    trainset = torchvision.datasets.FashionMNIST(root='./data', train=True, download=True, transform=transform)
    train_sampler = torch.utils.data.distributed.DistributedSampler(trainset, num_replicas=world_size, rank=rank)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=32, sampler=train_sampler, num_workers=2)

    num_epochs = 5
    for epoch in range(num_epochs):
        train_sampler.set_epoch(epoch)
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data[0].to(device), data[1].to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 200 == 199:
                print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 200:.3f}')
                running_loss = 0.0

    print('Finished Training')

    if rank == 0:
        torch.save(model.module.state_dict(), 'fashion_mnist_resnet18_distributed_mps.pt')
        print("Model saved as 'fashion_mnist_resnet18_distributed_mps.pt'")

    cleanup()

def main():
    world_size = torch.backends.mps.device_count()  
    mp.spawn(train, args=(world_size,), nprocs=world_size, join=True)

if __name__ == "__main__":
    main()