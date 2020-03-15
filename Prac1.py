import pydicom
from pydicom import dcmread
from pandastable import Table

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import pandas as pd
import numpy as np


def main():

    def ExtractInfo():
        print()
        print("Filename........................:", path)
        print("Storage type....................:", ds.SOPClassUID)
        print()

        pat_name = ds.PatientName
        display_name = pat_name.family_name + ", " + pat_name.given_name
        print("Patient's name..................:", display_name)
        print("Patient id......................:", ds.PatientID)
        print("Modality........................:", ds.Modality)
        print("Study Date......................:", ds.StudyDate)
        print("Manufacturer....................:", ds.Manufacturer)
        print("Manufacturer's Model Name.......:", ds.ManufacturerModelName)
        if 'PixelData' in ds:
            rows = int(ds.Rows)
            cols = int(ds.Columns)
            print("Image size......................: {rows:d} x {cols:d}, {size:d} bytes".format(
                rows=rows, cols=cols, size=len(ds.PixelData)))
            if 'PixelSpacing' in ds:
                print("Pixel spacing...................:", ds.PixelSpacing)

    def HeaderInfo():
        window = tk.Toplevel(root)
        window.title("Header Information")
        window.resizable(True, True)
        header_info = Table(window, dataframe=df)
        header_info.autoResizeColumns()
        header_info.show()

    def update_slice(self):
        pos = slice_selector.get()
        ax3.imshow(ds.pixel_array[pos, :, :], cmap=plt.cm.bone)
        if pos < img.shape[1]:
            ax1.imshow(ds.pixel_array[:, :, pos], cmap=plt.cm.bone)
            ax2.imshow(ds.pixel_array[:, pos, :], cmap=plt.cm.bone)
        else:
            ax1.imshow(ds.pixel_array[:, :, img.shape[2]-1], cmap=plt.cm.bone)
            ax2.imshow(ds.pixel_array[:, img.shape[1]-1, :], cmap=plt.cm.bone)
        fig.canvas.draw_idle()
        slice_pos = "Nº Slice: " + str(pos)
        label_slice.config(text=slice_pos)

    def onclick(event):
        if event.inaxes == ax1:
            if (event.x and event.y) is not None:
                sli = ds.pixel_array[:,:,pos]
                pixel_val = str(sli[int(event.ydata),int(event.xdata)])
                l2.config(text=pixel_val)
        elif event.inaxes == ax2:
            if (event.x and event.y) is not None:
                sli = ds.pixel_array[:,pos,:]
                pixel_val = str(sli[int(event.ydata), int(event.xdata)])
                l2.config(text=pixel_val)
        elif event.inaxes == ax3:
            if (event.x and event.y) is not None:
                sli = ds.pixel_array[pos, :, :]
                pixel_val = str(sli[int(event.ydata), int(event.xdata)])
                l2.config(text=pixel_val)

    #Read DICOM image path from keyboard imput
    path = input("Insert your DICOM image path: ")
    ds = dcmread(path)

    print(ds)
    ExtractInfo()
    pixel_len_mm = [float(ds.SliceThickness), float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1])]
    print()
    # Handling header information
    df = pd.DataFrame(ds.values())
    df[0] = df[0].apply(lambda x: pydicom.dataelem.DataElement_from_raw(x) if isinstance(x, pydicom.dataelem.RawDataElement) else x)
    df['name'] = df[0].apply(lambda x: x.name)
    df['value'] = df[0].apply(lambda x: x.value)
    df = df[['name', 'value']]

    img = np.flip(ds.pixel_array, axis=0)
    # Main Frame
    root = tk.Tk()

    #Header Information Button
    button1 = tk.Button(root,height=3,width=10, text ="Header", command = HeaderInfo)
    button1.pack(side = tk.RIGHT)

    #Displaying images
    fig = Figure(figsize=(9,7), dpi=100)
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    ax1.imshow(ds.pixel_array[:,:,0], cmap=plt.cm.bone)
    ax2.imshow(ds.pixel_array[:,0,:], cmap=plt.cm.bone)
    ax3.imshow(ds.pixel_array[0,:,:], cmap=plt.cm.bone)

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP , fill=tk.BOTH, expand=1)

    #TODO: get image contrast
    '''plt.hist(img.ravel(), bins=256, range=(-32768, 32767), fc='k', ec='k')
    plt.show()'''
    #hist = cv2.inRange(img, lowerBound, upperBound, None)
    #hist = cv2.bitwise_not(hist, hist)

    #Showing pixel numeric values on click
    l1 = tk.Label(root, text="Pixel Numeric Value")
    l2 = tk.Label(root, text="", width=40)
    l1.pack()
    l2.pack()
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    #Selecting slices
    pos=0
    slice_selector = tk.Scale(root,label="Slice selector", from_=0, to=ds.pixel_array.shape[0]-1, orient=tk.HORIZONTAL, length= 300,
                              command=update_slice)
    slice_selector.pack()
    label_slice = tk.Label(root)
    label_slice.pack()
    slice_pos = "Nº Slice: " + str(pos)
    label_slice.config(text=slice_pos)
    root.mainloop()


if __name__ == '__main__':

    main()
