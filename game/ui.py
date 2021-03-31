import pygame

from game.utils import Text, TextButton

class TowerInfoPanel:
	def __init__(self, screen, tower, pos):
		self.screen = screen
		self.tower = tower
		self.pos = pos

		self.panel = pygame.Surface((200, 400))
		self.panel.fill((54, 54, 54))
		
		if self.tower == None:
			return

		self.title = Text(self.tower.name, [self.pos[0] + 100, self.pos[1] + 15], 30, centered=True)

		self.make_info_text()
		self.make_upgrade_button()

		self.info_image = pygame.transform.scale(self.tower.info_image, (200,200))

	# updates tower info text, needs to be called when tower is upgraded so info panel is accurate
	def make_info_text(self):
		self.lvl_text = Text("Lvl " + str(self.tower.lvl + 1), [self.pos[0] + 100, self.pos[1] + 45], 15, centered=True)

		start_y = 265
		spacing = 25
		self.damage_text = Text("Damage: " + str(self.tower.damage), [self.pos[0] + 25, self.pos[1] + start_y], 20)
		self.range_text = Text("Range: " + str(self.tower.max_range), [self.pos[0] + 25, self.pos[1] + start_y + spacing], 20)
		self.speed_text = Text("Fire Speed: " + str(self.tower.fire_speed), [self.pos[0] + 25, self.pos[1] + start_y + spacing * 2], 20)

	def make_upgrade_button(self):
		if not self.tower.is_max_level():
			self.upgrade_button = TextButton("Promote", [self.pos[0] + 100, self.pos[1] + 360], 25, centered=True, color=(0, 255, 0))
		else:
			self.upgrade_button = Text("Max Level", [self.pos[0] + 100, self.pos[1] + 360], 25, centered=True, color=(255, 204, 0))

	def update(self):
		if self.tower == None:
			return

		if not self.tower.is_max_level() and self.upgrade_button.clicked:
			self.tower.upgrade()
			self.make_info_text()
			self.make_upgrade_button()

	def draw(self):
		self.screen.blit(self.panel, self.pos)

		if self.tower == None:
			return

		self.title.draw(self.screen)
		self.lvl_text.draw(self.screen)

		self.screen.blit(self.info_image, [self.pos[0], self.pos[1] + 60])

		self.damage_text.draw(self.screen)
		self.range_text.draw(self.screen)
		self.speed_text.draw(self.screen)

		self.upgrade_button.draw(self.screen)

		# drawing range circle
		pygame.draw.circle(self.screen, (255,255,255), self.tower.center_pos(), self.tower.max_range, width=1)