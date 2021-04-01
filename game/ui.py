import pygame

from game.utils import Text, TextButton, LinedText, Button
import game.load as load

class TowerInfoPanel:
	def __init__(self, screen, tower, pos):
		self.screen = screen
		self.tower = tower
		self.pos = pos

		self.panel = pygame.Surface((200, 450))
		self.panel.fill((54, 54, 54))
		
		if self.tower == None:
			return

		self.title = Text(self.tower.name, [self.pos[0] + 100, self.pos[1] + 15], 30, centered=True)

		self.make_info_text()
		self.make_upgrade_button()

		self.info_image = pygame.transform.scale(self.tower.info_image, (200,200))
		self.flavor_text = LinedText(self.tower.text, (self.pos[0] + 15, self.pos[1] + 260), 30, spacing=1, size=12)

	# updates tower info text, needs to be called when tower is upgraded so info panel is accurate
	def make_info_text(self):
		self.lvl_text = Text("Lvl " + str(self.tower.lvl + 1), [self.pos[0] + 100, self.pos[1] + 45], 15, centered=True)

		start_y = 310
		spacing = 25
		self.damage_text = Text("Damage: " + str(self.tower.damage), [self.pos[0] + 25, self.pos[1] + start_y], 20)
		self.range_text = Text("Range: " + str(self.tower.max_range), [self.pos[0] + 25, self.pos[1] + start_y + spacing], 20)
		self.speed_text = Text("Fire Speed: " + str(self.tower.fire_speed), [self.pos[0] + 25, self.pos[1] + start_y + spacing * 2], 20)

	def make_upgrade_button(self):
		if not self.tower.is_max_level():
			self.upgrade_button = TextButton("Promote", [self.pos[0] + 100, self.pos[1] + 400], 30, centered=True, color=(0, 255, 0))
			self.upgrade_cost_text = Text("Costs " + str(self.tower.upgrade_cost()) + " goodwill", [self.pos[0] + 100, self.pos[1] + 430], 12, centered=True)
		else:
			self.upgrade_button = Text("Max Level", [self.pos[0] + 100, self.pos[1] + 400], 30, centered=True, color=(255, 204, 0))
			self.upgrade_cost_text = Text("", self.pos)

	def update(self, currency):
		if self.tower == None:
			return currency

		cost = self.tower.upgrade_cost()
		if not self.tower.is_max_level() and self.upgrade_button.clicked and currency >= cost:
			self.tower.upgrade()
			self.make_info_text()
			self.make_upgrade_button()
			return currency - cost

		return currency

	def draw(self):
		self.screen.blit(self.panel, self.pos)

		if self.tower == None:
			return

		# drawing range circle
		pygame.draw.circle(self.screen, (255,255,255), self.tower.center_pos(), self.tower.max_range, width=1)
		self.screen.blit(self.panel, self.pos) # has to redraw so panel is on top of range circle

		self.title.draw(self.screen)
		self.lvl_text.draw(self.screen)

		self.screen.blit(self.info_image, [self.pos[0], self.pos[1] + 60])
		self.flavor_text.draw(self.screen)

		self.damage_text.draw(self.screen)
		self.range_text.draw(self.screen)
		self.speed_text.draw(self.screen)

		self.upgrade_button.draw(self.screen)
		self.upgrade_cost_text.draw(self.screen)

		
class BuyPanel:
	def __init__(self, screen, pos, towers):
		self.screen = screen
		self.pos = pos
		self.towers = towers

		self.panel = pygame.Surface((600, 175))
		self.panel.fill((54, 54, 54))

		self.buttons = []
		for i in range(len(self.towers)):
			b = BuyButton(self.screen, [self.pos[0] + 10 + 150 * i, self.pos[1] + 10], self.towers[i])
			self.buttons.append(b)

	def update(self):
		for b in self.buttons:
			b.update()

	def draw(self):
		self.screen.blit(self.panel, self.pos)

		for b in self.buttons:
			b.draw()

class BuyButton:
	def __init__(self, screen, pos, tower):
		self.screen = screen
		self.pos = pos
		self.tower = tower

		self.icon = pygame.transform.scale(tower.buy_icon, (136,100))
		self.text = Text("Deploy " + tower.name, [self.pos[0], self.pos[1] + 100], 20)
		self.cost_text = Text("Costs " + str(tower.cost[0]) + " goodwill", [self.pos[0] + 10, self.pos[1] + 125], 12)
		self.button = Button(pygame.Rect(self.pos, (136,150)))

	def update(self):
		self.button.draw(self.screen)

	def draw(self):
		self.screen.blit(self.icon, self.pos)
		self.text.draw(self.screen)
		self.cost_text.draw(self.screen)