import pygame as pg
from pygame.locals import Rect
from settings import *
from spells import *
from player import PlayerState
import os

class WSCREEN(pg.sprite.Sprite):
    """
    Parent class for non viewport screens
    inventory
    more?
    """
    def __init__(self, game, x, y):
        self.groups = game.screens
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.inspect_message = "A Screen for lookin..."
        self.name = "AScreen"

        # position should be fixed at the bottom
        self.image = pg.Surface((WIDTH, LOG_Y))
        self.image.fill(BLACK)
        self.x = S_X
        self.y = S_Y
        self.cur_x = self.x
        self.cur_y = self.y
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

        # keep track of the visible lines (these will get overridden by children)
        self.current_place = 0
        self.current_display = []

        # text stuff
        fonts = pg.font.get_fonts()
        self.font = pg.font.SysFont(fonts[0], S_TEXT_SIZE)
        self.selected_font = pg.font.SysFont(fonts[0], S_TEXT_SIZE + 5)
        self.header_buff = S_TEXT_SIZE * 2  # headers are two lines long
    
    def update(self):
        pass

    def drawt(self, screen):
        pass

class Inventory(WSCREEN):
    """
    Class handling the inventory screen
    """

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        # keep track of the visible lines
        self.current_place = 0
        # [[inventory], [spells], [states]]
        self.current_display = [[],[],[]]
        self.cur_x = x
        self.cur_y = y + self.header_buff
        self.starting = True
        self.select_buff = []

    class Entry(pg.sprite.Sprite):
        def __init__(self, game, obj, font, x, y):
            self.groups = game.screens
            pg.sprite.Sprite.__init__(self, self.groups)
            if type(obj) != str:
                self.obj = obj
                # if its a stat, display its value
                if obj in PlayerState.get_stats():
                    self.text = obj.get_display()
                else:
                    self.text = obj.name
            else:
                self.obj = None
                self.text = obj  # which its text in this case
            self.font = font
            self.image = pg.Surface(self.font.size(self.text))
            self.image.fill(BROWN)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y 
            self.selected = False  
        
        def check(self, mouse_pos):
            if self.rect.collidepoint(mouse_pos):
                return True
            return False
        
        def select(self, mouse_pos):
            if self.rect.collidepoint(mouse_pos):
                # check if ui element
                if self.obj:
                    self.selected = not self.selected
                    return True
            return False

        def inspect(self):
            if self.obj:
                return self.obj.inspect()
            else:
                return "A shiny UI element!"
        
        def drawt(self, screen, color):
            if self.selected:
                text = self.font.render(self.text, True, BLACK, YELLOW)
            else:
                text = self.font.render(self.text, True, color, (0, 0, 0))
            screen.blit(text, (self.rect.x, self.rect.y))
            
    
    def check(self, mouse_pos):
        msg = "Its either invisible or that is just the background of my inventory..."
        for category in self.current_display:
            for entry in category:
                if entry.check(mouse_pos):
                    if isinstance(entry.obj, KnownSpell):
                        self.game.player.equipped_spell = entry.obj
                    msg = entry.inspect()
        self.game.log.info(msg)
    
    def select(self, mouse_pos):
        selected = None
        for category in self.current_display:
            for entry in category:
                success = entry.select(mouse_pos)
                if success:
                    selected = entry
                    break
        if selected:
            if selected.obj:
                if isinstance(selected.obj, KnownSpell):
                    self.select_buff.append(selected)
            # if we have two spells, craft a new spell with them
            if len(self.select_buff) == 2:
                spell1 = self.select_buff[0]
                spell2 = self.select_buff[1]

                # get the name of the spell
                name = self.get_spell_info("Spell Name")

                # get the description of the spell and append
                # the elements
                desc = self.get_spell_info("Spell Description")
                new_elements = spell1.obj.elements + spell2.obj.elements
                desc += " " + str(new_elements)
                new_spell = KnownSpell(name=name, 
                                       elements=new_elements,
                                       description=desc)
                self.game.player.add_spell(new_spell)
                for s in self.select_buff:
                    s.selected = False
                self.select_buff = []
        else:
            pass
    
    def add_header(self, col, header):
            h1 = Inventory.Entry(self.game, header, self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            h2 = Inventory.Entry(self.game, "---------", self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            self.current_display[col].append(h1)
            self.current_display[col].append(h2)

    def update(self):
        """
        check the players inventory and update
        current display
        """
        # reset cur_x and cur_y
        self.cur_x = self.x
        self.cur_y = self.y
        # player inventory
        cur_inven = self.game.player.state.inventory
        # check if inventory has changed (+2 for headers)
        if len(cur_inven) + 2 != len(self.current_display[0]):
            # reset with header
            self.current_display[0] = []
            self.add_header(0, "Inventory")
            for item in cur_inven:
                e = Inventory.Entry(self.game, item, self.font, self.cur_x, self.cur_y)
                self.cur_y += S_LINE_DIST
                self.current_display[0].append(e)
        
        # reset
        self.cur_x += WIDTH/3
        self.cur_y = self.y  

        # spells
        cur_spells = self.game.player.spells
        if len(cur_spells) + 2 != len(self.current_display[1]):
            self.current_display[1] = []
            self.add_header(1, "Spells")
            for spell in cur_spells:
                e = Inventory.Entry(self.game, spell, self.font, self.cur_x, self.cur_y)
                self.cur_y += S_LINE_DIST
                self.current_display[1].append(e)
        
        # reset
        self.cur_x += (WIDTH/3)
        self.cur_y = self.y
        
        # stats
        stats = self.game.player.get_stats()
        self.current_display[2] = []
        self.add_header(2, "Stats")
        for stat in stats:
            e = Inventory.Entry(self.game, stat, self.font, self.cur_x, self.cur_y)
            self.cur_y += S_LINE_DIST
            self.current_display[2].append(e)

        # reset cur_x and cur_y
        self.cur_x = self.x
        self.cur_y = self.y
        self.starting = False

    def drawt(self, screen):
        # draw the black backdrop
        screen.blit(self.image, (self.x, self.y))

        # line for each item
        for item in self.current_display[0]:
            if item.obj and item.obj == self.game.player.equipped_item:
                item.drawt(screen, RED)
            else:
                item.drawt(screen, WHITE)

        # line for each spell
        for spell in self.current_display[1]:
            if spell.obj and spell.obj == self.game.player.equipped_spell:
                spell.drawt(screen, RED)
            else:
                spell.drawt(screen, WHITE)

        for stat in self.current_display[2]:
            stat.drawt(screen, WHITE)

        
    def get_spell_info(self, prompt):
        # set repeat rate to help text input
        pg.key.set_repeat(SPRINT_DELAY + 200, SPRINT_SPEED)
        start_text = prompt
        text = start_text
        font = pg.font.SysFont(None, 48)
        img = font.render(text, True, RED)
        
        bkg = pg.Surface(img.get_size())
        bkg.fill(BLACK)
        max_size = img.get_size()

        rect = img.get_rect()
        rect.center = (WIDTH/2, HEIGHT/2)
        cursor = Rect(rect.topright, (3, rect.height))

        done = False
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        done = True
                        break
                    if text == start_text:
                        text = ""
                    if event.key == pg.K_BACKSPACE:
                        if len(text)>0:
                            text = text[:-1]
                    else:
                        text += event.unicode
                    img = font.render(text, True, RED)
                    text_size = img.get_size()
                    if text_size > max_size:
                        max_size = text_size
                    bkg = pg.Surface(max_size)
                    bkg.fill(BLACK)
                    rect.size=text_size
                    cursor.topleft = rect.topright
            if done:
                break
            self.game.screen.blit(bkg, rect)
            self.game.screen.blit(img, rect)
            if time.time() % 1 > 0.5:
                pg.draw.rect(self.game.screen, RED, cursor)
            pg.display.update()
        
        # reset key rate
        pg.key.set_repeat(SPRINT_DELAY, SPRINT_SPEED)
        return text



        

