# config.py
INTRUDER_COOLDOWN    = 5     # seconds between intruder alerts per camera
AUTHORIZED_COOLDOWN  = 10    # seconds between authorized alerts per person
PROCESS_EVERY_N_FRAMES = 2   # only run recognition on every 2nd frame
ENCODING_RELOAD_INTERVAL = 300  # reload known faces from DB every 5 minutes

# CAMERAS = [
#     {
#         "id": "CAM_01",
#         "source": 0
#     },
#     {
#         "id": "CAM_02",
#         "source": 1
#     }
# ]