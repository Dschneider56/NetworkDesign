from Sender import Sender
from Receiver import Receiver
import numpy as np
import matplotlib.pyplot as plt

TRIALS = 3
TO_PERCENT = 0.65

dest = r'C:\\Users\\Roarke\\Desktop\\graphs\\'

corruption_rates = np.arange(0.0, TO_PERCENT, 0.05)
#delta_times = []
#delta_times_data = []
#delta_times_ack = []

def eval_reg_data():
    delta_times = []
    for trial in range(20):
        # time = []
        r = Receiver()
        c = Sender()  # Create sender object
        # times.append(c.delta_time)
        # print(c.delta_time)
        delta_times.append(c.delta_time)

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title(f"Average File Send Time over {20} Trials\nvs.\nNo Corruption")
    plt.xlabel("Trial number")
    plt.ylabel("Completion time (s)")

    plt.plot(range(20), delta_times)
    plt.savefig(dest + 'no_corruption.png')
    plt.close()
    delta_times = []
    #plt.show()

def eval_data_corrupt():
    delta_times_data = []
    for corruption_rate in corruption_rates:
        times = []
        for i in range(TRIALS):
            r = Receiver(data_percent_corrupt=corruption_rate)
            c = Sender()  # Create sender object
            times.append(c.delta_time)
            print(f'data corrupt trial # {i}: rate at {corruption_rate}')
        delta_times_data.append(np.mean(times))

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title(f"Average File Send Time over 10 Trials\nvs.\nCorruption Percentage of Data")
    plt.xlabel("Corruption Rate (percent of packets corrupt)")
    plt.ylabel("Average time (s)")
    plt.plot(corruption_rates, delta_times_data)
    plt.savefig(dest + 'data_corruption.png')
    plt.close()
    delta_times_data = []
    #plt.show()

def eval_ack_corrupt():
    delta_times_ack = []
    # Evaluate times for corrupt ack
    for corruption_rate in corruption_rates:
        times = []
        for i in range(TRIALS):
            r = Receiver(ack_percent_corrupt=corruption_rate)
            c = Sender()  # Create sender object

            times.append(c.delta_time)
            print(f'ack corrupt trial # {i}: rate at {corruption_rate}')
        delta_times_ack.append(np.mean(times))

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title("Average File Send Time over 10 Trials\nvs.\nCorruption Percentage of ACK bit")
    plt.xlabel("Corruption Rate (percent of packets corrupt)")
    plt.ylabel("Average time (s)")
    plt.plot(corruption_rates, delta_times_ack)
    plt.savefig(dest + 'ack_corruption.png')
    plt.close()
    delta_times_ack = []
    #plt.show()

def eval_data_loss():
    delta_times_data_loss = []
    # Evaluate data loss
    for corruption_rate in corruption_rates:
        times = []
        for i in range(TRIALS):
            r = Receiver()
            c = Sender(data_percent_loss=corruption_rate)  # Create sender object

            times.append(c.delta_time)
            print(f'data loss trial # {i}: rate at {corruption_rate}')
        delta_times_data_loss.append(np.mean(times))

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title(f"Average File Send Time over {TRIALS} Trials\nvs.\nLoss Percentage of Data")
    plt.xlabel("Loss Rate (percent of packets data lost)")
    plt.ylabel("Average time (s)")
    plt.plot(corruption_rates, delta_times_data_loss)
    plt.savefig(dest + 'data_loss.png')
    plt.close()
    delta_times_data_loss = []
    #plt.show()

def eval_ack_loss():
    delta_times_ack_loss = []
    # Evaluate data loss
    for corruption_rate in corruption_rates:
        times = []
        for i in range(TRIALS):
            r = Receiver()
            c = Sender(ack_percent_loss=corruption_rate)  # Create sender object
            print(f'ack loss trial # {i}: rate at {corruption_rate}')
            times.append(c.delta_time)
        delta_times_ack_loss.append(np.mean(times))

    plt.grid(color='black', linestyle=':', linewidth=1)
    plt.title("Average File Send Time over 10 Trials\nvs.\nLoss Percentage of ACK bit")
    plt.xlabel("Loss Rate (percent of packets ack lost)")
    plt.ylabel("Average time (s)")
    plt.plot(corruption_rates, delta_times_ack_loss)
    plt.savefig(dest + 'ack_loss.png')
    plt.close()
    delta_times_ack_loss = []
    #plt.show()

if __name__ == '__main__':

    #eval_reg_data()
   # eval_data_corrupt()
    eval_ack_corrupt()
    eval_data_loss()
    eval_ack_loss()






    #plt.close()
    # data

