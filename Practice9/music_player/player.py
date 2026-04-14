import pygame
import os

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.init()
WIDTH=800
HEIGHT=800
screen=pygame.display.set_mode((WIDTH, HEIGHT))
done=True
pygame.display.set_caption("🎵 Music player")
clock=pygame.time.Clock()

font_big = pygame.font.SysFont("consolas", 48, bold=True)
font_med = pygame.font.SysFont("consolas", 32)
font_small = pygame.font.SysFont("consolas", 24)
font_tiny = pygame.font.SysFont("consolas", 18)

BG = (10, 0, 30)
ACCENT = (0, 255, 204)
TEXT = (220, 255, 255)
HIGHLIGHT = (255, 255, 100)

folder="musics"

if not os.path.exists(folder):
    os.mkdir(folder)
    print("musics folder was created" )
    print("Add some tracks there")

tracks=[]
for file in os.listdir(folder):
    if file.lower().endswith(("mp3", "wav")):
        tracks.append(os.path.join(folder, file))
        
if not tracks:
    print(f"No music files in ./{folder}/")
    print("add some MP3 or WAV files and run again")
    track=[]
    
track_names = [os.path.basename(t) for t in tracks]
current_index = 0
is_playing = False
volume = 0.8
pygame.mixer.music.set_volume(volume)

print("\n🎹 Controls:")
print("   P = Play          S = Stop")
print("   N = Next          B = Previous")
print("   Space = Pause/Resume")
print("   ↑/↓ = Volume      ←/→ = Seek ±10s")
print("   Q = Quit\n")

while done:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            done=False
        if event.type==pygame.KEYDOWN:
            key=event.key
            
            if key==pygame.K_p:
                if not pygame.mixer.get_busy():
                    pygame.mixer.music.load(tracks[current_index])
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.unpause()
                is_playing = True
            elif key==pygame.K_s:
                pygame.mixer.music.stop()
                is_playing = False
            
            elif key==pygame.K_n:
                if tracks:
                    pygame.mixer.music.stop()
                    current_index = (current_index + 1) % len(tracks)
                    pygame.mixer.music.load(tracks[current_index])
                    pygame.mixer.music.play()
                    is_playing = True
            elif key==pygame.K_b:
                if tracks:
                    pygame.mixer.music.stop()
                    current_index=(current_index-1)%len(tracks)
                    pygame.mixer.music.load(tracks[current_index])
                    pygame.mixer.music.play()
                    is_playing=True
            elif key==pygame.K_q:
                done=False
            elif key == pygame.K_SPACE:    # Pause / Resume
                if pygame.mixer.music.get_busy():
                    if is_playing:
                        pygame.mixer.music.pause()
                        is_playing = False  # paused state
                    else:
                        pygame.mixer.music.unpause()
                        is_playing = True
            elif key == pygame.K_UP:
                volume = min(1.0, volume + 0.05)
                pygame.mixer.music.set_volume(volume)
            elif key == pygame.K_DOWN:
                volume = max(0.0, volume - 0.05)
                pygame.mixer.music.set_volume(volume)
            elif  key== pygame.K_RIGHT:
                if pygame.mixer.music.get_busy():
                    pos = pygame.mixer.music.get_pos() / 1000 + 10
                    try:
                        pygame.mixer.music.set_pos(pos)
                    except:
                        pass
            elif key == pygame.K_LEFT:
                if pygame.mixer.music.get_busy():
                    pos = max(0, pygame.mixer.music.get_pos() / 1000 - 10)
                    try:
                        pygame.mixer.music.set_pos(pos)
                    except:
                        pass
                
    if is_playing and tracks and not pygame.mixer.music.get_busy():
        current_index = (current_index + 1) % len(tracks)
        pygame.mixer.music.load(tracks[current_index])
        pygame.mixer.music.play()
        
    screen.fill(BG)

    
    title = font_big.render("MUSIC player", True, ACCENT)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    if not tracks:
        no_music = font_med.render("NO MUSIC FILES IN ./music/", True, (255, 100, 100))
        screen.blit(no_music, (WIDTH // 2 - no_music.get_width() // 2, HEIGHT // 2))
    else:
        current_name = track_names[current_index]
        track_text = font_med.render(f"NOW PLAYING:", True, TEXT)
        name_text = font_small.render(current_name, True, HIGHLIGHT)
        screen.blit(track_text, (60, 120))
        screen.blit(name_text, (60, 160))

        # Progress bar
        if pygame.mixer.music.get_busy():
            elapsed_ms = pygame.mixer.music.get_pos()
            elapsed = elapsed_ms / 1000
            try:
                total = pygame.mixer.Sound(tracks[current_index]).get_length()
            except:
                total = 180  # fallback

            progress = min(elapsed / total, 1.0) if total > 0 else 0

            pygame.draw.rect(screen, (50, 50, 80), (60, 220, 780, 20))
            
            pygame.draw.rect(screen, ACCENT, (60, 220, 780 * progress, 20))

            
            elapsed_str = f"{int(elapsed//60)}:{int(elapsed%60):02d}"
            total_str = f"{int(total//60)}:{int(total%60):02d}"
            time_text = font_small.render(f"{elapsed_str} / {total_str}", True, TEXT)
            screen.blit(time_text, (60, 255))
        else:
            pygame.draw.rect(screen, (50, 50, 80), (60, 220, 780, 20))

        y = 300
        for i, name in enumerate(track_names):
            color = HIGHLIGHT if i == current_index else TEXT
            prefix = "▶ " if i == current_index else f"{i+1:02d}. "
            txt = font_small.render(prefix + name, True, color)
            screen.blit(txt, (60, y))
            y += 35
            if y > HEIGHT - 140:
                break

    
    help_y = HEIGHT - 110
    controls = [("P", "PLAY"), ("S", "STOP"), ("N", "NEXT"), ("B", "BACK"), ("Q", "QUIT")]
    for i, (k, label) in enumerate(controls):
        x = 60 + i * 150
        pygame.draw.rect(screen, (30, 0, 60), (x, help_y, 120, 65), border_radius=8)
        pygame.draw.rect(screen, ACCENT, (x, help_y, 120, 65), 4, border_radius=8)
        key_surf = font_med.render(k, True, (255, 255, 255))
        screen.blit(key_surf, (x + 50, help_y + 8))
        lbl_surf = font_tiny.render(label, True, ACCENT)
        screen.blit(lbl_surf, (x + 30, help_y + 42))

    
    vol_text = font_small.render(f"Vol: {int(volume*100)}%", True, TEXT)
    screen.blit(vol_text, (WIDTH - 180, HEIGHT - 50))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
print("\n👋 Music player closed. Thanks for listening!")