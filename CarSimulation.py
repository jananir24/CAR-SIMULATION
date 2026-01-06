import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# Car class
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 70
        self.angle = 0
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.friction = 0.1
        self.rotation_speed = 5
        
        # Sensors for obstacle detection
        self.sensors = []
        self.sensor_length = 150
        self.sensor_angles = [-60, -30, 0, 30, 60]  # Degrees relative to car direction
        
        # AI control
        self.auto_drive = True
        self.collision = False
        
    def update(self, obstacles):
        # Detect obstacles with sensors
        self.sensors = []
        for angle_offset in self.sensor_angles:
            sensor_angle = math.radians(self.angle + angle_offset)
            sensor_x = self.x + math.cos(sensor_angle) * self.sensor_length
            sensor_y = self.y + math.sin(sensor_angle) * self.sensor_length
            
            # Check for collision with obstacles
            distance = self.sensor_length
            for obs in obstacles:
                if obs.collides_with_line(self.x, self.y, sensor_x, sensor_y):
                    # Calculate actual distance to obstacle
                    dx = obs.x + obs.width/2 - self.x
                    dy = obs.y + obs.height/2 - self.y
                    dist = math.sqrt(dx**2 + dy**2)
                    distance = min(distance, dist)
            
            self.sensors.append({
                'angle': sensor_angle,
                'distance': distance,
                'end_x': self.x + math.cos(sensor_angle) * distance,
                'end_y': self.y + math.sin(sensor_angle) * distance
            })
        
        # Auto-driving AI logic
        if self.auto_drive:
            self.ai_control(obstacles)
        
        # Apply friction
        if self.speed > 0:
            self.speed -= self.friction
        elif self.speed < 0:
            self.speed += self.friction
        
        # Limit speed
        self.speed = max(-self.max_speed/2, min(self.speed, self.max_speed))
        
        # Move car
        rad_angle = math.radians(self.angle)
        self.x += math.cos(rad_angle) * self.speed
        self.y += math.sin(rad_angle) * self.speed
        
        # Keep car on screen
        self.x = max(0, min(self.x, WIDTH))
        self.y = max(0, min(self.y, HEIGHT))
        
        # Check collision with obstacles
        self.collision = False
        car_rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, 
                               self.width, self.height)
        for obs in obstacles:
            if car_rect.colliderect(obs.get_rect()):
                self.collision = True
                self.speed = 0
    
    def ai_control(self, obstacles):
        # Simple AI: avoid obstacles and move forward
        sensor_values = [s['distance'] for s in self.sensors]
        
        # Get front, left, and right sensor readings
        left_sensor = sensor_values[0]
        left_mid = sensor_values[1]
        center_sensor = sensor_values[2]
        right_mid = sensor_values[3]
        right_sensor = sensor_values[4]
        
        # Obstacle detection threshold
        danger_distance = 80
        
        # Decision making
        if center_sensor < danger_distance:
            # Obstacle ahead - turn away from it
            if left_sensor > right_sensor:
                self.angle -= self.rotation_speed
            else:
                self.angle += self.rotation_speed
            self.speed *= 0.5  # Slow down
        elif left_mid < danger_distance:
            # Obstacle on left - turn right
            self.angle += self.rotation_speed * 0.8
        elif right_mid < danger_distance:
            # Obstacle on right - turn left
            self.angle -= self.rotation_speed * 0.8
        else:
            # Clear path - accelerate forward
            self.speed += self.acceleration
        
        # Slight randomness to explore
        if random.random() < 0.02:
            self.angle += random.choice([-1, 1]) * 2
    
    def manual_control(self, keys):
        # Manual keyboard control
        if keys[pygame.K_UP]:
            self.speed += self.acceleration
        if keys[pygame.K_DOWN]:
            self.speed -= self.acceleration
        if keys[pygame.K_LEFT]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle += self.rotation_speed
    
    def draw(self, screen):
        # Draw car
        color = RED if self.collision else (BLUE if self.auto_drive else GREEN)
        
        # Rotate car sprite
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, color, (0, 0, self.width, self.height))
        pygame.draw.rect(car_surface, BLACK, (0, 0, self.width, self.height), 2)
        
        # Rotate
        rotated_car = pygame.transform.rotate(car_surface, -self.angle)
        rect = rotated_car.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car, rect.topleft)
        
        # Draw sensors
        for sensor in self.sensors:
            # Color based on distance
            if sensor['distance'] < 50:
                sensor_color = RED
            elif sensor['distance'] < 100:
                sensor_color = YELLOW
            else:
                sensor_color = GREEN
            
            pygame.draw.line(screen, sensor_color, 
                           (self.x, self.y), 
                           (sensor['end_x'], sensor['end_y']), 2)
            pygame.draw.circle(screen, sensor_color, 
                             (int(sensor['end_x']), int(sensor['end_y'])), 5)

# Obstacle class
class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def collides_with_line(self, x1, y1, x2, y2):
        # Simple line-rectangle collision
        rect = self.get_rect()
        return rect.clipline(x1, y1, x2, y2)
    
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

# Main function
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Self-Driving Car Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Create car
    car = Car(100, HEIGHT // 2)
    
    # Create obstacles
    obstacles = [
        Obstacle(300, 200, 100, 150),
        Obstacle(600, 400, 150, 100),
        Obstacle(900, 100, 80, 200),
        Obstacle(400, 500, 200, 80),
        Obstacle(700, 600, 100, 100),
    ]
    
    running = True
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    car.auto_drive = not car.auto_drive
                if event.key == pygame.K_r:
                    car.x, car.y = 100, HEIGHT // 2
                    car.angle = 0
                    car.speed = 0
                    car.collision = False
        
        # Get keyboard input for manual control
        keys = pygame.key.get_pressed()
        if not car.auto_drive:
            car.manual_control(keys)
        
        # Update
        car.update(obstacles)
        
        # Draw
        screen.fill(WHITE)
        
        # Draw road boundaries
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT), 5)
        
        # Draw obstacles
        for obs in obstacles:
            obs.draw(screen)
        
        # Draw car
        car.draw(screen)
        
        # Draw UI
        mode_text = "AUTO-DRIVE" if car.auto_drive else "MANUAL"
        mode_color = BLUE if car.auto_drive else GREEN
        text = font.render(mode_text, True, mode_color)
        screen.blit(text, (10, 10))
        
        # Instructions
        instructions = [
            "SPACE: Toggle Auto/Manual",
            "R: Reset Car",
            "Arrows: Manual Control"
        ]
        for i, inst in enumerate(instructions):
            text = small_font.render(inst, True, BLACK)
            screen.blit(text, (10, 60 + i * 25))
        
        # Collision warning
        if car.collision:
            warning = font.render("COLLISION!", True, RED)
            screen.blit(warning, (WIDTH // 2 - 80, 10))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()