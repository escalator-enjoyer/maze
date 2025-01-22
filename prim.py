import pygame
import random
import heapq

width, height = 1000, 750
FPS_DISPLAY = 120
FPS_MOVEMENT = 30

# 1 is how fast it would be with the player's movement
dijkstra_slowness = 1.8 # 1.7 is like very difficult and <1.6 is basically impossible, 2 is beatable

visualize_dijkstra = False
path_pause = 1

running = False
game_over = False
player_moved = False

grid_width, grid_height = 40, 30
cell_size = 20
max_history_length = 15

offset_x = (width - grid_width * cell_size) // 2
offset_y = (height - grid_height * cell_size) // 2

colors = {
  'black': (20, 20, 20),
  'white': (230, 230, 230),
  'gray': (50, 50, 50),
  'pink': (247, 140, 255),
  'orange': (255, 200, 140),
  'green': (140, 255, 140),
}

pygame.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Maze RNG")
clock = pygame.time.Clock()

class Player:
  def __init__(self, x, y, moved=False):
    self.x = x
    self.y = y
    self.move_timer = 0
    self.history = []
    self.moved = moved

  def move(self, dx, dy, maze):
    global player_moved
    if not self.moved or not player_moved:
      self.moved = True
      player_moved = True
    if 0 <= self.x + dx < grid_width and 0 <= self.y + dy < grid_height:
      if not maze[self.y + dy][self.x + dx]:
        self.history.append((self.x, self.y))
        if len(self.history) > max_history_length:
          self.history.pop(0)
        self.x += dx
        self.y += dy

  def update(self, maze, dt, end_position):
    self.move_timer += dt
    if self.move_timer >= 1000 / FPS_MOVEMENT:
      keys = pygame.key.get_pressed()
      if keys[pygame.K_w]:
        self.move(0, -1, maze)
      if keys[pygame.K_a]:
        self.move(-1, 0, maze)
      if keys[pygame.K_s]:
        self.move(0, 1, maze)
      if keys[pygame.K_d]:
        self.move(1, 0, maze)
      self.move_timer = 0

    if (self.x, self.y) == end_position:
      return True
    return False

  def draw(self, surface):
    pygame.draw.rect(
      surface, colors['pink'],
      (self.x * cell_size + offset_x, self.y * cell_size + offset_y, cell_size, cell_size)
    )
  
  def draw_trail(self, surface):
    for hx, hy in self.history:
      darker_pink = tuple(max(0, int(c * 0.6)) for c in colors['pink'])
      pygame.draw.rect(
        surface, darker_pink,
        (hx * cell_size + offset_x, hy * cell_size + offset_y, cell_size, cell_size)
      )

class DijkstraPlayer:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.path = []
    self.path2 = []
    self.history = []
    self.move_timer = 0

  def find_path(self, maze, start, end):
    heap = [(0, start)]
    distances = {start: 0}
    previous = {start: None}
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    visited = []

    while heap:
      current_distance, current_position = heapq.heappop(heap)
      if current_position == end:
        break

      for dx, dy in directions:
        neighbor = (current_position[0] + dx, current_position[1] + dy)
        if 0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height and not maze[neighbor[1]][neighbor[0]]:
          distance = current_distance + 1
          if distance < distances.get(neighbor, float('inf')):
            distances[neighbor] = distance
            priority = distance
            heapq.heappush(heap, (priority, neighbor))
            previous[neighbor] = current_position
      
      visited.append(current_position)
      if visualize_dijkstra:
        draw_maze(maze, end)
        dark_orange = tuple(max(0, int(c * 0.3)) for c in colors['orange'])
        for thing in visited:
          pygame.draw.rect(
            screen, dark_orange,
            (thing[0] * cell_size + offset_x, thing[1] * cell_size + offset_y, cell_size, cell_size)
          )
        pygame.display.flip()
        process_inputs()
        clock.tick(FPS_MOVEMENT * 2)

    path = []
    step = end
    while step:
      path.append(step)
      step = previous[step]
      if visualize_dijkstra:
        for thing in path:
          pygame.draw.rect(
            screen, colors['orange'],
            (thing[0] * cell_size + offset_x, thing[1] * cell_size + offset_y, cell_size, cell_size)
          )
        pygame.display.flip()
        process_inputs()
        clock.tick(FPS_MOVEMENT * 2)
    if visualize_dijkstra:
      for x in range(path_pause):
        process_inputs()
        clock.tick(1/path_pause)
    path.reverse()
    return path
  
  def draw_path(self):
    if not self.path2:
      return
    
    dark_green = tuple(max(0, int(c * 0.25)) for c in colors['green'])
    for x, y in self.path2[0:-1]:
      pygame.draw.rect(
        screen, dark_green,
        (x * cell_size + offset_x, y * cell_size + offset_y, cell_size, cell_size)
      )

  def update(self, maze, dt, end_position):
    self.move_timer += dt
    if self.move_timer >= 1000 / FPS_MOVEMENT * dijkstra_slowness:
      if not self.path:
        self.path = self.find_path(maze, (self.x, self.y), end_position)

      if self.path:
        next_step = self.path.pop(0)
        self.history.append((self.x, self.y))
        if len(self.history) > max_history_length:
          self.history.pop(0)
        self.x, self.y = next_step
      self.move_timer = 0

    if (self.x, self.y) == end_position:
      return True
    return False

  def draw(self, surface):
    pygame.draw.rect(
      surface, colors['orange'],
      (self.x * cell_size + offset_x, self.y * cell_size + offset_y, cell_size, cell_size)
    )
  
  def draw_trail(self, surface):
    for hx, hy in self.history:
      darker_orange = tuple(max(0, int(c * 0.6)) for c in colors['orange'])
      pygame.draw.rect(
        surface, darker_orange,
        (hx * cell_size + offset_x, hy * cell_size + offset_y, cell_size, cell_size)
      )

def create_maze():
  maze = [[1 for _ in range(grid_width)] for _ in range(grid_height)]
  stack = []
  visited = set()

  def add_walls(x, y):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    random.shuffle(directions)
    for dx, dy in directions:
      nx, ny = x + dx * 2, y + dy * 2
      if 0 <= nx < grid_width and 0 <= ny < grid_height and (nx, ny) not in visited:
        stack.append((x, y, nx, ny))

  start_x, start_y = random.randint(0, grid_width - 1), random.randint(0, grid_height - 1)
  start_x -= start_x % 2
  start_y -= start_y % 2

  maze[start_y][start_x] = 0
  visited.add((start_x, start_y))
  add_walls(start_x, start_y)

  end_x, end_y = start_x, start_y

  while stack:
    x, y, nx, ny = stack.pop()
    if (nx, ny) not in visited:
      maze[(y + ny) // 2][(x + nx) // 2] = 0
      maze[ny][nx] = 0
      visited.add((nx, ny))
      add_walls(nx, ny)

      draw_maze(maze)
      pygame.display.flip()
      process_inputs()
      clock.tick(FPS_DISPLAY)

  end_x, end_y = random.choice(list(visited))

  return maze, (start_x, start_y), (end_x, end_y)

def draw_maze(maze, end_position=None):
  screen.fill(colors['black'])
  for y in range(grid_height):
    for x in range(grid_width):
      color = colors['gray'] if maze[y][x] == 0 else colors['black']
      pygame.draw.rect(
         screen, color, 
        (x * cell_size + offset_x, y * cell_size + offset_y, cell_size, cell_size)
      )
  if end_position:
    ex, ey = end_position
    pygame.draw.rect(
      screen, colors['green'],
      (ex * cell_size + offset_x, ey * cell_size + offset_y, cell_size, cell_size)
    )

def process_inputs():
  global screen, width, height, offset_x, offset_y, visualize_dijkstra, running, game_over, player_moved
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_v and (game_over or not player_moved):
          visualize_dijkstra = not visualize_dijkstra
      if event.type == pygame.VIDEORESIZE:
        width, height = event.size
        offset_x = (width - grid_width * cell_size) // 2
        offset_y = (height - grid_height * cell_size) // 2
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

def main():
  maze, start_position, end_position = create_maze()
  player = Player(*start_position)
  dijkstra_player = DijkstraPlayer(*start_position)

  global screen, width, height, offset_x, offset_y, visualize_dijkstra, running, game_over, player_moved
  
  game_over = False
  running = True
  player_moved = False
  show_path = False
  while running:
    dt = clock.tick(FPS_DISPLAY)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
          maze, start_position, end_position = create_maze()
          player = Player(*start_position)
          dijkstra_player = DijkstraPlayer(*start_position)
          game_over = False
        elif event.key == pygame.K_v:
          visualize_dijkstra = not visualize_dijkstra
        elif event.key == pygame.K_t:
          show_path = not show_path
      if event.type == pygame.VIDEORESIZE:
        width, height = event.size
        offset_x = (width - grid_width * cell_size) // 2
        offset_y = (height - grid_height * cell_size) // 2
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

    if not game_over:
      if visualize_dijkstra:
        dijkstra_player.path = dijkstra_player.find_path(maze, start_position, end_position)
        visualize_dijkstra = False
      game_over = player.update(maze, dt, end_position)
      if player.moved:
        dijkstra_player.update(maze, dt, end_position)
    

    draw_maze(maze, end_position)
    if show_path:
      if not dijkstra_player.path2:
        dijkstra_player.path2 = dijkstra_player.find_path(maze, (player.x, player.y), end_position)
      dijkstra_player.draw_path()
    player.draw_trail(screen)
    dijkstra_player.draw_trail(screen)
    dijkstra_player.draw(screen)
    player.draw(screen)

    if game_over:
      font = pygame.font.Font(None, 74)
      text = font.render("R to Restart", True, colors['white'])
      screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
      show_path = False
      visualize_dijkstra = False

    pygame.display.flip()

  pygame.quit()

if __name__ == "__main__":
  main()
