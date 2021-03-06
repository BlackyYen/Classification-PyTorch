import torch
import numpy
from pathlib import Path
from torchvision import datasets, models, transforms
import torch.nn as nn
import torchvision
import numpy as np
import matplotlib.pyplot as plt
from tools.plotcm import plot_confusion_matrix
from sklearn.metrics import confusion_matrix
from tqdm import tqdm
import os
device = torch.device("cuda")

#設計超參數
batch_size = 8
num_workers = 0

model = torch.load('./classification/pretrained_model/resnext101_32x8d.pth')
fc_features = model.fc.in_features
model.fc = nn.Linear(fc_features, 20)
model.to(device)
model.load_state_dict(torch.load('./classification/logs/best_weight.pth'))
model.eval()

PATH_test = r"D:\training_dataset\simpsons\test"
# TEST = Path(PATH_test)

test_transforms = transforms.Compose([
    transforms.Resize((192, 192)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
test_data = datasets.ImageFolder(PATH_test, transform=test_transforms)

test_loader = torch.utils.data.DataLoader(test_data,
                                          batch_size=batch_size,
                                          num_workers=num_workers)
test_data_iter = iter(test_loader)
test_image, test_label = test_data_iter.next()

criterion = nn.CrossEntropyLoss()
criterion = criterion.to(device)

# monitor test loss and accuracy
test_loss = 0.
correct = 0.
total = 0.
pred_cm = torch.empty(125, 8)
model.eval()

pred_cm = torch.tensor([]).to(device)
for data, target in tqdm(test_loader):
    # move to GPU
    data, target = data.to(device), target.to(device)
    # forward pass: compute predicted outputs by passing inputs to the model
    output = model(data)
    # calculate the loss
    loss = criterion(output, target)
    # convert output probabilities to predicted class
    pred = output.data.max(1, keepdim=True)[1]
    pred_cm = torch.cat((pred_cm, pred), dim=0)
    # compare predictions to true label
    correct += np.sum(
        np.squeeze(pred.eq(target.data.view_as(pred))).cpu().numpy())
    total += data.size(0)

print('Test Accuracy: ', (correct / total))

print(test_data)
# print(pred_cm)
# a = torch.tensor(test_data.targets)
# b = pred_cm.cpu().argmax(dim=1)
# print(a)
# print(b)
cm = confusion_matrix(torch.tensor(test_data.targets), pred_cm.cpu())
print(type(cm))

dataset_dir = PATH_test
classes = os.listdir(dataset_dir)
plt.figure(figsize=(2, 2))
plot_confusion_matrix(cm,
                      classes,
                      normalize=False,
                      title='Confusion matrix',
                      cmap=plt.cm.Blues)
