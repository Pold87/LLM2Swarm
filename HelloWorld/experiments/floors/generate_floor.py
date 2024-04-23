#!/usr/bin/env python3

"""
This script creates a random floor layout/patterns and saves the
pattern as .png image and as .csv file.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import os
from math import sqrt
from random import uniform
import os
arena_size = os.environ["ARENADIM"]
print(arena_size)

np.random.seed(seed=1)

percentage_white = 0.25
tiles_per_side_list = [22, 31, 38]
#tiles_per_side_list = [10]

def create_shuffled_matrix(tiles_per_side):

    total_tiles = tiles_per_side ** 2
    percentage_black = 1 - percentage_white
    total_white = total_tiles * percentage_white
    total_black = total_tiles * percentage_black
    
    white_tiles_array = np.zeros(int(total_white))
    black_tiles_array = np.ones(int(total_black))
    total_tiles_array = np.append(white_tiles_array, black_tiles_array)


    np.random.shuffle(total_tiles_array)

    # Check if one tile is missing
    if (len(total_tiles_array) == total_tiles - 1):
        total_tiles_array = np.append(total_tiles_array, 1.0)
        print("Missing one tile")
    X = total_tiles_array.reshape((tiles_per_side, tiles_per_side), order='F')
        
    fig = plt.figure()
    plt.xticks([])
    plt.yticks([])
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                        hspace = 0, wspace = 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.imshow(X, cmap='Greys',  interpolation='nearest')
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                        hspace = 0, wspace = 0)
    plt.margins(0,0)

    # Save as png
    img_name = str(tiles_per_side) + ".png"
    print("Saving image to " + img_name)
    plt.savefig(img_name, bbox_inches = 'tight')

    # Save as pdf
    img_name_pdf = str(tiles_per_side) + ".pdf"
    print("Saving image to " + img_name_pdf)
    plt.savefig(img_name_pdf, bbox_inches = 'tight')

    # Save as svg
    img_name_svg = str(tiles_per_side) + ".svg"
    print("Saving image to " + img_name_svg)
    plt.savefig(img_name_svg, bbox_inches = 'tight')    
    
    # Save as csv
    csv_name = str(tiles_per_side) + ".csv"
    np.savetxt(csv_name, total_tiles_array, delimiter='\n', fmt='%d')
    
    # Remove white space around the image
    os.system('convert ' + img_name +  ' -trim ' + img_name)
    print("Saving CSV layout file to " + csv_name)
    

def create_market_resources(market_percent_size, number_resources, quality_range):  

    cm = 1/2.54
    fig, ax = plt.subplots(figsize=(10*cm, 10*cm))
    plt.xticks([])
    plt.yticks([])
    plt.gca().set_axis_off()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    # ax.add_patch(Rectangle((0.5-market_percent_size/2, 0.5-market_percent_size/2), market_percent_size, market_percent_size, color="yellow"))
    # f = open('resources.txt', 'w+')
    # for i in range(0,number_resources):
    #     circle_quality = round(uniform(quality_range[0],quality_range[1]), 2)
    #     circle_center = (uniform(0,1), uniform(0,1))
    #     ax.add_patch(Circle(circle_center, circle_quality, color="red"))
    #     f.write(' '.join([str(round(x,2)) for x in circle_center])+ ' ' + str(round(circle_quality,2))+'\n')
    

    # Save as png
    img_name = "market" + ".png"
    print("Saving image to " + img_name)
    plt.savefig(img_name, bbox_inches = 'tight')


def main_shuffled_matrix():
    for tiles_per_side in tiles_per_side_list:
        create_shuffled_matrix(tiles_per_side)
        

def main_market():
    create_market_resources(0.2,5,[0.02,0.1])

if __name__ == "__main__":
    # main_shuffled_matrix()
    main_market()

