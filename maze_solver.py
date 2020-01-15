from PIL import Image, ImageDraw
from math import inf
from sys import argv

SOURCE = 1
DEST = 2

class Node:
    def __init__(self, pos, tile_type=None):
        self.parent = self.left = self.right = self.down = self.up = None
        self.left_dist = self.right_dist = self.down_dist = self.up_dist = inf
        self.type = tile_type
        self.dist = 0 if tile_type == SOURCE else inf
        self.visited = False
        self.pos = pos

def nearest_node(nodes):
    """Returns the unvisited node with the least distance"""
    result = None
    least_dist = inf

    for node in nodes:
        if not node.visited and node.dist < least_dist:
            result = node
            least_dist = node.dist
            
    return result


def get_nodes(image):
    """Returns a list nodes in an image. Image must use black for walls and white for paths, and
       the image must be bordered by black. Corridors must be 1-pixel wide."""

    # Retrieve pixels and convert to a 1 bit image (black = false, white = true).
    pixels = list(image.convert('L').getdata())
    pixels = [list(map(lambda p: p > 127, pixels[i * image.width:(i + 1) * image.width])) for i in range(image.height)]

    nodes = []
    found_source = False
    
    # Begin forming nodes
    for y in range(image.height):
        for x in range(image.width):
            if pixels[y][x]:    # If vertically/horizontally 3 tiles there's only 1 wall -> you know to place a node.
                borders = x in (0, image.width - 1) or y in (0, image.height - 1)
                if x > 0 and x + 1 < image.width and (pixels[y][x - 1] != False) ^ (pixels[y][x + 1] != False) or \
                   y > 0 and y + 1 < image.height and (pixels[y - 1][x] != False) ^ (pixels[y + 1][x] != False) or \
                   borders:

                    # Create node and init to either source, dest, or path
                    if borders:
                        pixels[y][x] = Node((x,y), SOURCE if not found_source else DEST)
                        found_source = True
                    else:
                        pixels[y][x] = Node((x,y))
                    nodes.append(pixels[y][x])

                    # Go left to form relations
                    for i in range(x - 1, -1, -1):
                        if isinstance(pixels[y][i], Node):
                            pixels[y][i].right = pixels[y][x]
                            pixels[y][x].left = pixels[y][i]
                            pixels[y][i].right_dist = pixels[y][x].left_dist = x - i
                            break
                        elif not pixels[y][i]:
                            break
                        
                    # Go up to form relations
                    for i in range(y - 1, -1, -1):
                        if isinstance(pixels[i][x], Node):
                            pixels[i][x].down = pixels[y][x]
                            pixels[y][x].up = pixels[i][x]
                            pixels[i][x].down_dist = pixels[y][x].up_dist = y - i
                            break
                        elif not pixels[i][x]:
                            break

    return nodes


def solve(image):
    return dijkstra(get_nodes(image))


def dijkstra(nodes):
    """Finds the least expensive path to a destination node.
       Returns a reverse chained list of nodes beginning with the destination node."""
    
    node = nearest_node(nodes)
    while node and node.type != DEST:
        
        # Update neighboring distances & set as parent
        if node.up and node.up_dist + node.dist < node.up.dist:
            node.up.dist = node.up_dist + node.dist
            node.up.parent = node

        if node.down and node.down_dist + node.dist < node.down.dist:
            node.down.dist = node.down_dist + node.dist
            node.down.parent = node

        if node.left and node.left_dist + node.dist < node.left.dist:
            node.left.dist = node.left_dist + node.dist
            node.left.parent = node

        if node.right and node.right_dist + node.dist < node.right.dist:
            node.right.dist = node.right_dist + node.dist
            node.right.parent = node

        # Mark as visited and proceed to the next nearest node to the source
        node.visited = True
        node = nearest_node(nodes)

    return node


def draw_route(image):
    """Draws a route to solve a maze. Returns the modified image."""

    image = image.convert("RGB")
    dest = solve(image)
    draw = ImageDraw.Draw(image)

    while dest and dest.parent:
        draw.line(dest.pos + dest.parent.pos, fill=(0, 255, 0))
        dest = dest.parent

    return image
    


if __name__ == "__main__":

    if len(argv) <= 1:
        exit()

    im = Image.open(argv[1])
    if '-w' in argv or '--write' in argv:
        draw_route(im).save(argv[2] if len(argv) > 2 and argv[2][0] != '-' else "result." + argv[1].split('.')[1])
    else:
        draw_route(im).show()
        
    
    
