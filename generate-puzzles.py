import argparse
import os
import random

from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor

def is_valid(puzzle, x, y, num):
    num = str(num)
    # Check row and column
    for i in range(9):
        if puzzle[x][i] == num or puzzle[i][y] == num:
            return False

    # Check box
    box_x, box_y = (x // 3) * 3, (y // 3) * 3
    for i in range(3):
        for j in range(3):
            if puzzle[box_x + i][box_y + j] == num:
                return False

    return True

def solve_sudoku(puzzle):
    for x in range(9):
        for y in range(9):
            if puzzle[x][y] == '.':
                for num in random.sample(range(1, 10), 9):
                    if is_valid(puzzle, x, y, num):
                        puzzle[x][y] = str(num)
                        if solve_sudoku(puzzle):
                            return True
                        puzzle[x][y] = '.'
                return False
    return True

def generate_solved_puzzle():
    puzzle = [['.' for _ in range(9)] for _ in range(9)]
    solve_sudoku(puzzle)
    return puzzle

def generate_puzzle():
    puzzle = generate_solved_puzzle()
    for i in range(9):
        for j in range(9):
            if random.random() < 0.5:
                puzzle[i][j] = '.'
    return puzzle

def generate_puzzle_wrapper(index, number_of_puzzles):
    print(f'\rGenerating puzzles... {(index + 1) / number_of_puzzles * 100:.4f}% complete', end='')
    return generate_puzzle()

def list_fonts():    
    fonts = os.listdir('fonts/')
    # Filter out non-font files
    fonts = [font for font in fonts if font.endswith('.ttf') or font.endswith('.otf')]
    return fonts  

def generate_puzzle_images_wrapper(puzzle_count, puzzles, img_dir, text_dir, available_fonts):
    print(f'\rGenerating puzzle images... {(puzzle_count + 1) / len(puzzles) * 100:.4f}% complete', end='')
    puzzle = puzzles[puzzle_count]
    filename = f"puzzle_{puzzle_count}.png"
    with open(f'{img_dir}/{filename}', 'wb') as f:
        generate_image(puzzle, f, available_fonts)
    
    filename = f"puzzle_{puzzle_count}.txt"
    with open(f'{text_dir}/{filename}', 'w') as f:
        for row in puzzle:
            f.write(' '.join(row) + '\n')

def high_contrast_color(bg_color):
    # Calculate perceived brightness
    brightness = (0.299*bg_color[0] + 0.587*bg_color[1] + 0.114*bg_color[2]) / 255
    # Choose high contrast color with moderated intensity
    if brightness > 0.5:
        # Darker color but not black
        return (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
    else:
        # Lighter color but not white
        return (random.randint(155, 255), random.randint(155, 255), random.randint(155, 255))

def random_color(exclude_extremes=True):
    if exclude_extremes:
        # Avoiding very dark and very light colors
        return tuple(random.randint(32, 223) for _ in range(3))
    else:
        return tuple(random.randint(0, 255) for _ in range(3))

def generate_image(puzzle, filepath, available_fonts, img_width=500, img_height=500, padding=10, font_size=42, random_modifier=True):
    if random_modifier:
        modifier = 1 + random.random()
    else:
        modifier = 1

    img_width = int(img_width * modifier)
    img_height = int(img_height * modifier)
    padding = int(padding * modifier)
    cell_size = (img_width - 2 * padding) // 9
    line_width_thin = int(2 * modifier)
    line_width_thick = int(5 * modifier)

    # Generate a random background color
    bg_color = random_color()
    img = Image.new('RGB', (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)

    font_choice = random.choice(available_fonts)
    try:
        font = ImageFont.truetype(f'fonts/{font_choice}', int(font_size * modifier))
    except IOError:
        print(f'Error loading font {font_choice}, using default font')
        font = ImageFont.load_default()

    # Draw the grid and numbers
    for x in range(9):
        for y in range(9):
            text = puzzle[x][y]
            if text != '.':
                # Calculate cell's top left corner
                cell_x = padding + y * cell_size
                cell_y = padding + x * cell_size

                # Determine high-contrast text color
                text_color = high_contrast_color(bg_color)

                # Measure text size for centering
                text_size = draw.textbbox((0, 0), text, font=font)
                text_width = text_size[2] - text_size[0]
                text_height = text_size[3] - text_size[1]
                text_x = cell_x + (cell_size - text_width) / 2
                text_y = cell_y + (cell_size - text_height) / 2

                draw.text((text_x, text_y), text, fill=text_color, font=font)

    img.save(filepath, 'PNG')


def save_text_wrapper(puzzle_count, puzzles, text_dir):
    print(f'\rSaving text files... {(puzzle_count + 1) / len(puzzles) * 100:.4f}% complete', end='')
    puzzle = puzzles[puzzle_count]
    filename = f"puzzle_{puzzle_count}.txt"
    with open(f'{text_dir}/{filename}', 'w') as f:
        for row in puzzle:
            f.write(' '.join(row) + '\n')



def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate sudoku puzzles')
    parser.add_argument('n', type=int, help='Number of puzzles to generate')
    parser.add_argument('--imgs', type=str, help='Output directory for img files')
    parser.add_argument('--text', type=str, help='Output directory for text files')
    args = parser.parse_args()

    img_dir = 'generated'
    text_dir = 'textversion'

    available_fonts = list_fonts()

    if args.imgs:
        img_dir = args.imgs
    if args.text:
        text_dir = args.text

    # Generate puzzles using multithreading
    with ThreadPoolExecutor() as executor:
        puzzles = list(executor.map(generate_puzzle_wrapper, range(args.n), [args.n] * args.n))

    print(f'\rGenerating puzzles... 100.0000% complete', end='')
    print()

    # Verify generated directory exists
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # Verify textversion directory exists
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)

    puzzle_count = 0

    # Generate images using multithreading
    with ThreadPoolExecutor() as executor:
        list(executor.map(generate_puzzle_images_wrapper, range(args.n), [puzzles] * args.n, [img_dir] * args.n, [text_dir] * args.n, [available_fonts] * args.n))

    print(f'\rGenerating puzzle images... 100.0000% complete', end='')
    print()

    # Save text files using multithreading
    with ThreadPoolExecutor() as executor:
        list(executor.map(save_text_wrapper, range(args.n), [puzzles] * args.n, [text_dir] * args.n))

    print(f'\rSaving text files... 100.0000% complete', end='')
    print()
    print('Done')


if __name__ == '__main__':
    main()