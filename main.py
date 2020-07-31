try:
  import carla
except Exception as e:
  print('cannot import carla python library, please install into the python path now')
  exit(1)
import subprocess, os
import argparse
import time
import signal
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
IM_HEIGHT = 1080
IM_WIDTH = 1920
PLT_IMG_HANDLER = None
CURRENT_CAM_IMG = None
argparser = argparse.ArgumentParser(description=__doc__)
argparser.add_argument('--host', metavar='H', default='127.0.0.1', help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument('-p', '--port', metavar='P', default=2000, type=int, help='TCP port to listen to (default: 2000)')
argparser.add_argument('--map', default='Town05', type=str, help='choose map')
args = argparser.parse_args()

try:
  print('setting up client...')
  client = carla.Client(args.host, args.port)
  client.set_timeout(2.0)
  client.load_world(args.map)
  client.reload_world()
  print('loading world complete')
  # process = subprocess.Popen(['python','spawn_npc.py', '-n', '80', '--sync']) #spawn some npc
except Exception as e:
  print('error in creating the client, make sure your simulator is launched, try to increase --launch-carla-timeout value or manually launch the simulator, and use --manual-launch-carla flag:')
  print(str(e))
  exit(1)
def processImg(image):
  global PLT_IMG_HANDLER
  global CURRENT_CAM_IMG
  i = np.array(image.raw_data)
  i = i.reshape((IM_HEIGHT, IM_WIDTH, 4))
  i = i[:, :, :3]
  CURRENT_CAM_IMG = i
  # image.save_to_disk('image.png')
  return i/255.0
def imgUpdate(i):
  global PLT_IMG_HANDLER
  if not PLT_IMG_HANDLER:
    PLT_IMG_HANDLER = plt.imshow(CURRENT_CAM_IMG)
  else:
    PLT_IMG_HANDLER.set_data(CURRENT_CAM_IMG)
print('successfully connected to Carla')
world = client.get_world()
settings = world.get_settings()
world.apply_settings(settings)
map = world.get_map()
bp = world.get_blueprint_library().find('sensor.camera.rgb')
bp.set_attribute('image_size_x', str(IM_WIDTH))
bp.set_attribute('image_size_y', str(IM_HEIGHT))
bp.set_attribute('fov', '110')
# Set the time in seconds between sensor captures
bp.set_attribute('sensor_tick', '0.2')
transform = carla.Transform(carla.Location(x=-65.0, y=3.0, z=6.0), carla.Rotation(yaw=180.0, pitch=-30.0))
sensor = world.spawn_actor(bp, transform)
sensor.listen(processImg)
ani = FuncAnimation(plt.gcf(), imgUpdate, interval=50)
plt.show()
# image.raw_data

# # Default format (depends on the camera PostProcessing but always a numpy array).
# image.data

# # numpy BGRA array.
# image_converter.to_bgra_array(image)

# # numpy RGB array.
# image_converter.to_rgb_array(image)
time.sleep(2)
while True:
  world.wait_for_tick()
  print(world.get_actors())