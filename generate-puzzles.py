import argparse
import os
import random

from PIL import Image, ImageDraw, ImageFont

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


def list_fonts():    
    fonts = os.listdir('fonts/')
    # Filter out non-font files
    fonts = [font for font in fonts if font.endswith('.ttf') or font.endswith('.otf')]
    return fonts  


def generate_image(puzzle, filepath, img_width=500, img_height=500, padding=10, font_size=42, random_modifier=True):
    if random_modifier:
        modifier = 1 + random.random()
    else:
        modifier = 1

    img_width = (int)(img_width * modifier)
    img_height = (int)(img_height * modifier)
    padding = (int)(padding * modifier)
    cell_size = (img_width - 2 * padding) // 9
    line_width_thin = (int)(2 * modifier)
    line_width_thick = (int)(5 * modifier)
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)

    available_fonts = list_fonts()
    font_choice = random.choice(available_fonts)

    try:
        font = ImageFont.truetype(f'fonts/{font_choice}', (int)(font_size * modifier))
    except IOError:
        print(f'Error loading font {font_choice}, using default font')
        font = ImageFont.load_default()

    # Draw thin lines
    for i in range(10):
        line_position = padding + i * cell_size
        draw.line((line_position, padding, line_position, img_height - padding), fill='black', width=line_width_thin)
        draw.line((padding, line_position, img_width - padding, line_position), fill='black', width=line_width_thin)

    # Draw thick lines for main grid
    for i in range(0, img_width - 2 * padding, 3 * cell_size):
        line_position = padding + i
        draw.line((line_position, padding, line_position, img_height - padding), fill='black', width=line_width_thick)
        draw.line((padding, line_position, img_width - padding, line_position), fill='black', width=line_width_thick)

    # Draw numbers
    for x in range(9):
        for y in range(9):
            if puzzle[x][y] != '.':
                text = puzzle[x][y]
                # Measure text size for centering
                text_size = draw.textbbox((0, 0), text, font=font)
                text_width = text_size[2] - text_size[0]
                text_height = text_size[3] - text_size[1]
                text_x = padding + y * cell_size + (cell_size - text_width) / 2
                text_y = padding + x * cell_size + (cell_size - text_height) / 2
                draw.text((text_x, text_y), text, fill='black', font=font)

    img.save(filepath, 'PNG')



def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate sudoku puzzles')
    parser.add_argument('n', type=int, help='Number of puzzles to generate')
    args = parser.parse_args()

    # Generate puzzles
    puzzles = []
    for i in range(0, args.n):
        puzzles.append(generate_solved_puzzle())

    # Verify generated directory exists
    if not os.path.exists('generated'):
        os.makedirs('generated')

    puzzle_count = 0
    for puzzle in puzzles:
        # Generate image
        with open(f'generated/puzzle_{puzzle_count}.png', 'wb') as f:
            generate_image(puzzle, f)
        puzzle_count += 1


if __name__ == '__main__':
    main()