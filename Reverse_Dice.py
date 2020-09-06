class ReverseDice:

    # generates random numbers using k as the number of dice, n as the highest number and N as the number of dice
    @staticmethod
    def generate_rolls_to_sum(total, k, n, N):
        roller = np.random.randint(low=1, high=n + 1, size=(N, k))
        idx = np.where(roller.sum(axis=1) == total)
        return roller[idx, :]

    # sends requests to generator function until the correct total is returned
    def get_roll(self, total, k, n):
        while True:
            z = self.generate_rolls_to_sum(total, k, n, 1)
            if z.size > 0:
                break
        return z.flatten().tolist()

    # main function
    def only_dice(self, roll, result, modifier=0):
            
            # checks for valid input
            if roll is None:
                print('Roll formula invalid or None')
                return
            if result - modifier < 1:
                print('result - modifier is less than 1')
                return

            # separates formula into individual dice rolls
            roll = roll.replace('+', '~')
            roll = roll.replace('-', '~-')
            roll = roll.split('~')

            # finds max roll for each dice and separates the number of dice from the number of sides
            roll_grouped = []
            max_rolls = []
            for val in roll:
                split_val = val.split('d')
                if not split_val[0]:
                    split_val[0] = 1
                elif split_val[0] == '-':
                    split_val[0] = -1
                formatted_val = [int(split_val[0]), int(split_val[1])]
                max_rolls.append(formatted_val[0] * formatted_val[1])
                roll_grouped.append(formatted_val)

            # assigns result to each dice roll group based on weight vs total result
            dice_nums = []
            for max_roll in max_rolls:
                percent = max_roll / ((sum(max_rolls)) + modifier)
                mod = modifier * percent
                dice_nums.append(math.ceil((result - mod) * percent))

            # checks to make sure value given to a roll is no more than the max and no less than the min roll
            for n in range(len(dice_nums)):
                if dice_nums[n] < roll_grouped[n][0]:
                    dice_nums[n] = roll_grouped[n][0]
                elif dice_nums[n] > max_rolls[n]:
                    dice_nums[n] = max_rolls[n]

            # distributes any remaining values after rounding
            if sum(dice_nums) != result - modifier:
                i = result - modifier - sum(dice_nums)
                while True:
                    for l in range(len(dice_nums)):
                        if i == 0:
                            break
                        elif i >= 1:
                            if dice_nums[l] < max_rolls[l]:
                                dice_nums[l] = dice_nums[l] + 1
                                i -= 1
                        else:
                            if dice_nums[l] > roll_grouped[l][0]:
                                dice_nums[l] = dice_nums[l] - 1
                                i += 1
                    if i == 0:
                        break

            # finds a matching roll randomly, inverts any negatives
            results_list = []
            for x in range(len(dice_nums)):
                if dice_nums[x] > 0:
                    matched_roll = self.get_roll(dice_nums[x], roll_grouped[x][0], roll_grouped[x][1])
                else:
                    invert_dice = roll_grouped[x][0] * -1
                    invert_result = dice_nums[x] * -1
                    matched_roll = self.get_roll(invert_result, invert_dice, roll_grouped[x][1])
                for r in matched_roll:
                    results_list.append([roll_grouped[x][1], r])
            return results_list
