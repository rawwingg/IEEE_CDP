import numpy as np
import matplotlib.pyplot as plt
import lgpio
import time
#servo start
SERVO_GPIO = 18
PWM_FREQ   = 50

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, SERVO_GPIO)  # <-- this is the key line

def set_servo_angle(angle):
    angle    = max(0, min(180, angle))
    pulse_us = int(500 + (angle / 180.0) * 2000)
    lgpio.tx_servo(h, SERVO_GPIO, pulse_us, PWM_FREQ)
    print(f"Servo: {angle} deg (pulse: {pulse_us}us)")

#servo end
xmin, xmax = -2, 2
ymin, ymax = -2, 2

rng = np.random.default_rng()

# Target
target_length = 0.25
target_x1 = -target_length / 2
target_x2 = target_length / 2
target_center = np.array([0, ymax])

# Object with plane
object_pos = np.array([
    rng.uniform(xmin, 0),
    rng.uniform(ymin, 0)
])

# Ball on right wall
ball_pos = np.array([
    xmax,
    rng.uniform(ymin, ymax)
])

# Vectors from object
object_to_target = target_center - object_pos
object_to_ball = ball_pos - object_pos

# Unit vectors
u_target = object_to_target / np.linalg.norm(object_to_target)
u_ball = object_to_ball / np.linalg.norm(object_to_ball)

# Normal points halfway between target and ball directions
normal = u_target + u_ball
normal = normal / np.linalg.norm(normal)

rotation_angle_deg = np.rad2deg(np.arctan2(normal[1], normal[0]))

print("Object rotation angle:", rotation_angle_deg, "degrees")

# Test
set_servo_angle(rotation_angle_deg)
time.sleep(1)

lgpio.gpiochip_close(h)

# Tangent plane is perpendicular to normal
tangent = np.array([
    normal[1],
    -normal[0]
])

plane_length = 0.5
p1 = object_pos - (plane_length / 2) * tangent
p2 = object_pos + (plane_length / 2) * tangent

# For drawing vector from ball to object
ball_to_object = object_pos - ball_pos

fig, ax = plt.subplots(figsize=(7, 7))

# Arena
ax.plot([xmin, xmax, xmax, xmin, xmin],
        [ymin, ymin, ymax, ymax, ymin],
        linewidth=2)

# Axes
ax.axhline(0, linewidth=1)
ax.axvline(0, linewidth=1)

# Target
ax.plot([target_x1, target_x2], [ymax, ymax],
        linewidth=6,
        solid_capstyle="butt",
        label="Target")

# Object
ax.scatter(object_pos[0], object_pos[1],
           s=100,
           label="Object")

# Ball
ax.scatter(ball_pos[0], ball_pos[1],
           s=100,
           label="Ball")

# Tangent plane
ax.plot([p1[0], p2[0]],
        [p1[1], p2[1]],
        linewidth=3,
        label="Tangent plane")

# Normal vector
normal_length = 0.6
ax.arrow(object_pos[0], object_pos[1],
         normal_length * normal[0],
         normal_length * normal[1],
         head_width=0.06,
         length_includes_head=True,
         label="Normal")

# Vector from object to target
ax.arrow(object_pos[0], object_pos[1],
         object_to_target[0],
         object_to_target[1],
         head_width=0.06,
         length_includes_head=True,
         label="Object to target")

# Vector from ball to object
ax.arrow(ball_pos[0], ball_pos[1],
         ball_to_object[0],
         ball_to_object[1],
         head_width=0.06,
         length_includes_head=True,
         label="Ball to object")

ax.set_xlim(xmin - 0.2, xmax + 0.2)
ax.set_ylim(ymin - 0.2, ymax + 0.2)
ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("x position (m)")
ax.set_ylabel("y position (m)")
ax.set_title("Normal Bisects Target and Ball Directions")
ax.grid(True)
ax.legend(loc="lower right")

plt.show()

print("Object position:", object_pos)
print("Ball position:", ball_pos)
print("Target center:", target_center)
print("Normal vector:", normal)
