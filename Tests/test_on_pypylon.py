# imports
import os
os.environ["PYLON_CAMEMU"] = "3"
from pypylon import genicam
from pypylon import pylon
import sys
import numpy as np
import scipy.misc
import cv2

# preface
exitCode = 0
maxCamerasToUse = 4
countOfImagesToGrab = 1
try:

    # get the transport layer factory
    tlFactory = pylon.TlFactory.GetInstance()

    devices = tlFactory.EnumerateDevices()
    if len(devices) == 0:
        raise pylon.RUNTIME_EXCEPTION("No camera present")

    cameras = pylon.InstantCameraArray(min(len(devices), maxCamerasToUse))

    for ii, cam in enumerate(cameras):
        cam.Attach(tlFactory.CreateDevice(devices[ii]))

        print(cam.GetDeviceInfo().GetModelName(), "-", cam.GetDeviceInfo().GetSerialNumber())
        
        
        # set parameters
        # pixel format
        print(cam.PixelFormat.GetValue())
        cam.PixelFormat.SetValue("Mono12")
        print(cam.PixelFormat.GetValue())
        # exposure time
        cam.ExposureAuto.SetValue("Off")
        cam.ExposureTime.SetValue(100.0)
        # gain
        cam.GainAuto.SetValue("Off")
        cam.Gain.SetValue(1.0)
        
        cam.Gain.SetValue(float(11))
        print(cam.Gain.GetValue())
        print(cam.ExposureTime.GetValue())

        # start grabbing
        cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        grabResult = cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        cameraContextValue = grabResult.GetCameraContext()
        print("Grab succeeded: ", grabResult.GrabSucceeded())

        if grabResult.GrabSucceeded() == True:
            img = grabResult.GetArray()
            path = "D:\Python\PyBaslerMultiCam\PyBaslerMultiCam"
            filename = cam.GetDeviceInfo().GetSerialNumber()
            filetyp = "png"
            fullpath = os.path.join(path, filename + "." + filetyp)
            scipy.misc.imsave(fullpath, img)

        cam.StopGrabbing()

except genicam.GenericException as e:
    # error handling
    print("An exception occurred.", e.GetDescription())
    exitCode = 1

sys.exit(exitCode)