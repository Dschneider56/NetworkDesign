from UDPClient import UDPClient
from UDPServer import UDPServer
import numpy as np
import matplotlib.pyplot as plt

TRIALS = 10
TO_PERCENT = 0.65

if __name__ == '__main__':
    corruption_rates = np.arange(0.0, TO_PERCENT, 0.05)
    delta_times = []
    delta_times_data = []
    delta_times_ack = []
    UDPServer()  # Create server thread

    # Evaluate times for regular data
    for trial in range(TRIALS):
        #time = []
        c = UDPClient()  # Create client object
        #times.append(c.delta_time)
        #print(c.delta_time)
        delta_times.append(c.delta_time)

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title(f"Average File Send Time over {TRIALS} Trials\nvs.\nNo Corruption")
    plt.xlabel("Trial number")
    plt.ylabel("Completion time (s)")

    plt.plot(range(TRIALS), delta_times)
    plt.show()

    # Evaluate times for corrupt data
    for corruption_rate in corruption_rates:
        times = []
        for i in range(TRIALS):
            c = UDPClient(data_percent_corrupt=corruption_rate)  # Create client object
            times.append(c.delta_time)
        delta_times_data.append(np.mean(times))

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title(f"Average File Send Time over {TRIALS} Trials\nvs.\nCorruption Percentage of Data")
    plt.xlabel("Corruption Rate (percent of packets corrupt)")
    plt.ylabel("Average time (s)")
    plt.plot(corruption_rates, delta_times_data)
    plt.show()

    # Evaluate times for corrupt ack
    for corruption_rate in corruption_rates:
        times = []
        for i in range(TRIALS):
            c = UDPClient(ack_percent_corrupt=corruption_rate)  # Create client object

            times.append(c.delta_time)
        delta_times_ack.append(np.mean(times))

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title("Average File Send Time over 10 Trials\nvs.\nCorruption Percentage of ACK bit")
    plt.xlabel("Corruption Rate (percent of packets corrupt)")
    plt.ylabel("Average time (s)")
    plt.plot(corruption_rates, delta_times_ack)
    plt.show()
