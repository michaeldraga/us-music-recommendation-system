import json

def parse_stored_scores():
    scores = []
    with open('scores.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split(',')
            eps = float(line[0].split(':')[1])
            min_samples = int(line[1].split(':')[1])
            metric = line[2].split(':')[1].strip()
            score = float(line[3].split(':')[1])
            n_labels = int(line[4].split(':')[1])
            scores.append([eps, min_samples, metric, score, n_labels])
    return scores

scores = parse_stored_scores()

eps_values = [i/10 for i in range(1, 10)]

# create a list of the min_samples values to test
min_samples_values = [i for i in range(1, 10)]

# create a list to store the different metrics
metrics = ['manhattan', 'euclidean']

full_data = []
index = 0
for metric in metrics:
    print('metric: {}'.format(metric))
    # loop through the eps values
    for i in eps_values:
        print('eps: {}'.format(i))
        # loop through the min_samples values
        for j in min_samples_values:
            print('min_sample: {}'.format(j))
            eps_1, min_samples_1, metric_1, score_1, n_labels_1 = scores[index]

            if metric != metric_1 or eps_1 != i or min_samples_1 != j:
                print('='*50)
                full_data.append([i, j, metric, 0, 0])   
                continue
            

            full_data.append([i, j, metric_1, score_1, n_labels_1])
            index += 1

with open('full_scores.txt', 'w') as f:
    for row in full_data:
        f.write(','.join([str(i) for i in row]) + '\n')

print(full_data)
print(len(full_data) == len(eps_values) * len(min_samples_values) * len(metrics))
