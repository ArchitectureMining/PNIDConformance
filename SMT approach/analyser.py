import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def analyse_time(results_file, horizontal):
    data = pd.read_csv("results/" + results_file, index_col=0)
    folder = "results/images/" 

    plt.rcParams["figure.figsize"] = [10,12]
    fig = plt.figure()
    fig.subplots_adjust()
    ax1 = fig.add_subplot(211)
    
    ax1.set_ylabel('avg conversion time (s)')
    plt.xticks(data[horizontal].tolist(), data[horizontal].tolist())
    if results_file == "times - Easy (model+trace increase).csv":
        ax1.set_xlabel(horizontal + ", model size")
    else:
        ax1.set_xlabel(horizontal)
    
    plt.plot(data[horizontal], data["avg_conv_time"])
    plt.savefig(folder + results_file + " [" + horizontal + "," + "avg_conv_time" + "].png", bbox_inches='tight')
    plt.clf()

    plt.rcParams["figure.figsize"] = [10,12]
    fig = plt.figure()
    fig.subplots_adjust()
    ax1 = fig.add_subplot(211)
    if results_file == "times - Easy (model+trace increase).csv":
        ax1.set_xlabel(horizontal + ", model size")
    else:
        ax1.set_xlabel(horizontal)
    ax1.set_ylabel('avg encode time (s)')
    plt.xticks(data[horizontal].tolist(), data[horizontal].tolist())
    plt.plot(data[horizontal], data["avg_encode_time"])
    plt.savefig(folder + results_file + " [" + horizontal + "," + "avg_encode_time" + "].png", bbox_inches='tight')
    plt.clf()

    plt.rcParams["figure.figsize"] = [10,12]
    fig = plt.figure()
    fig.subplots_adjust()
    ax1 = fig.add_subplot(211)
    if results_file == "times - Easy (model+trace increase).csv":
        ax1.set_xlabel(horizontal + ", model size")
    else:
        ax1.set_xlabel(horizontal)
    ax1.set_ylabel('avg solve time (s)')
    plt.xticks(data[horizontal].tolist(), data[horizontal].tolist())
    plt.plot(data[horizontal], data["avg_solve_time"])
    plt.savefig(folder + results_file + " [" + horizontal + "," + "avg_solve_time" + "].png", bbox_inches='tight')
    plt.clf()

    plt.rcParams["figure.figsize"] = [10,12]
    fig = plt.figure()
    fig.subplots_adjust()
    ax1 = fig.add_subplot(211)
    if results_file == "times - Easy (model+trace increase).csv":
        ax1.set_xlabel(horizontal + ", model size")
    else:
        ax1.set_xlabel(horizontal)
    ax1.set_ylabel('avg total time (s)')
    plt.xticks(data[horizontal].tolist(), data[horizontal].tolist())
    plt.plot(data[horizontal], data["avg_total_time"])
    plt.savefig(folder + results_file + " [" + horizontal + "," + "avg_total_time" + "].png", bbox_inches='tight')
    plt.clf()
    
