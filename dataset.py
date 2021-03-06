import numpy as np
import pandas as pd
from PIL import Image
from torch.utils.data.dataset import Dataset

from utils import get_frame


class DenoisingDataset(Dataset):
    """Class for torch Dataset forming."""
    def __init__(self, dataset, 
                       image_size, frame_size, overlay_size,
                       phase='train', transform=None):
        """Constructor."""
        self.dataset = dataset[dataset['phase']==phase]
        self.image_size = image_size
        self.frame_size = frame_size
        self.overlay_size = overlay_size
        self.frames_number = self.get_frames_number()
        self.transform = transform

    def __getitem__(self, index):
        image_index = index // self.frames_number
        frame_index = index % self.frames_number
        
        path_to_image = self.dataset.iloc[image_index]['image']
        np_image = np.array(Image.open(path_to_image).convert('L').resize(self.image_size))
        frame = get_frame(np_image[..., np.newaxis],
                          frame_size=self.frame_size, overlay_size=self.overlay_size,
                          index=frame_index)
        
        if self.do_transform():
            frame = self.transform(frame)
        
        label = self.dataset.iloc[image_index]['label']
        
        return (frame, label)

    def __len__(self):
        return len(self.dataset) * self.frames_number
    
    def get_frames_number(self):
        width, height = self.image_size
        frame_y, frame_x = self.frame_size
        overlay_y, overlay_x = self.overlay_size
        
        columns_number = (width - overlay_y) // (frame_y - overlay_y)
        if (width - overlay_y) % (frame_y - overlay_y) != 0:
            columns_number += 1
    
        rows_number = (height - overlay_x) // (frame_x - overlay_x)
        if (height - overlay_x) % (frame_x - overlay_x) != 0:
            rows_number += 1
            
        return columns_number * rows_number

    def do_transform(self):
        return self.transform is not None
