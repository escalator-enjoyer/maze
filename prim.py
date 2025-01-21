import pygame
import random
import heapq

WIDTH, HEIGHT = 800, 600
FPS_DISPLAY = 120
FPS_MOVEMENT = 30

grid_width, grid_height = 40, 30
cell_size = 20
max_history_length = 10

colors = {
  'black': (20, 20, 20),
  'white': (230, 230, 230),
  'gray': (50, 50, 50),
  'pink': (247, 140, 255),
  'orange': (255, 200, 140),
  'green': (140, 255, 140),
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze RNG")
clock = pygame.time.Clock()

class Player:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.move_timer = 0
    self.history = []

  def move(self, dx, dy, maze):
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
      (self.x * cell_size, self.y * cell_size, cell_size, cell_size)
    )
  
  def draw_trail(self, surface):
    for hx, hy in self.history:
      darker_pink = tuple(max(0, int(c * 0.6)) for c in colors['pink'])
      pygame.draw.rect(
        surface, darker_pink,
        (hx * cell_size, hy * cell_size, cell_size, cell_size)
      )

class DijkstraPlayer:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.path = []
    self.history = []
    self.move_timer = 0

  def find_path(self, maze, start, end):
    heap = [(0, start)]
    distances = {start: 0}
    previous = {start: None}
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

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

    path = []
    step = end
    while step:
      path.append(step)
      step = previous[step]
    path.reverse()
    self.path = path

  def update(self, maze, dt, end_position):
    self.move_timer += dt
    if self.move_timer >= 1000 / FPS_MOVEMENT * 2:
      if not self.path:
        self.find_path(maze, (self.x, self.y), end_position)

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
      (self.x * cell_size, self.y * cell_size, cell_size, cell_size)
    )
  
  def draw_trail(self, surface):
    for hx, hy in self.history:
      darker_orange = tuple(max(0, int(c * 0.6)) for c in colors['orange'])
      pygame.draw.rect(
        surface, darker_orange,
        (hx * cell_size, hy * cell_size, cell_size, cell_size)
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
      clock.tick(FPS_DISPLAY)

  end_x, end_y = random.choice(list(visited))

  return maze, (start_x, start_y), (end_x, end_y)

def draw_maze(maze, end_position=None):
  screen.fill(colors['black'])
  for y in range(grid_height):
    for x in range(grid_width):
      color = colors['gray'] if maze[y][x] == 0 else colors['black']
      pygame.draw.rect(
        screen, color, (x * cell_size, y * cell_size, cell_size, cell_size)
      )
  if end_position:
    ex, ey = end_position
    pygame.draw.rect(
      screen, colors['green'],
      (ex * cell_size, ey * cell_size, cell_size, cell_size)
    )

def main():
  maze, start_position, end_position = create_maze()
  player = Player(*start_position)
  dijkstra_player = DijkstraPlayer(*start_position)

  running = True
  game_over = False
  while running:
    dt = clock.tick(FPS_DISPLAY)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
        maze, start_position, end_position = create_maze()
        player = Player(*start_position)
        dijkstra_player = DijkstraPlayer(*start_position)
        game_over = False

    if not game_over:
      game_over = player.update(maze, dt, end_position)
      dijkstra_player.update(maze, dt, end_position)

    draw_maze(maze, end_position)
    player.draw_trail(screen)
    dijkstra_player.draw_trail(screen)
    dijkstra_player.draw(screen)
    player.draw(screen)

    if game_over:
      font = pygame.font.Font(None, 74)
      text = font.render("R to Restart", True, colors['white'])
      screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    pygame.display.flip()

  pygame.quit()

if __name__ == "__main__":
  main()
