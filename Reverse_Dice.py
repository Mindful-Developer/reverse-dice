import numpy as np
import math
import re
from numba import njit


class ReverseDice:
    def __init__(self, formula):
        dice_pattern = r'((?:\d*?[dgprb]\d+)[^]]*?(?:\d*?[dgprb]\d+)?)?([+-]\d*)?\s?=\s?(\-?\d*)'
        match = re.search(dice_pattern, formula)

        roll = match.group(1)
        modifier = int(match.group(2)) if match.group(2) else 0
        result = int(match.group(3))

        if roll is None or result - modifier < 1:
            return

        change_characters = ['g', 'p', 'r', 'b', 'k']
        for character in change_characters:
            roll = roll.replace(character, 'd')

        print(self.only_dice(roll, result, modifier))

    # generates random numbers using k as the number of dice, n as the highest number and N as the number of dice
    @staticmethod
    @njit
    def generate_rolls_to_sum(total, number_of_dice, number_of_sides):
        while True:
            roller = np.random.randint(low=1, high=number_of_sides + 1, size=(1, number_of_dice))
            idx = np.where(roller.sum(axis=1) == total)
            if roller[idx].size > 0:
                break
        return roller

    # sends requests to generator and computes harder fringe cases
    def get_roll(self, total, number_of_dice, number_of_sides):
        dice_list = []

        # fringe cases to skip rolling
        if number_of_dice * number_of_sides == total:
            for x in range(number_of_dice):
                dice_list.append(number_of_sides)
            return dice_list
        elif total == number_of_dice * number_of_sides - 1:
            for x in range(number_of_dice - 1):
                dice_list.append(number_of_sides)
            dice_list.append(number_of_sides - 1)
            return dice_list
        elif total == number_of_dice:
            for x in range(number_of_dice):
                dice_list.append(1)
            return dice_list
        elif total == number_of_dice + 1:
            for x in range(number_of_dice - 1):
                dice_list.append(1)
            dice_list.append(2)
            return dice_list

        dice_list = self.generate_rolls_to_sum(total, number_of_dice, number_of_sides)

        return dice_list.flatten().tolist()

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

        # distributes any remaining values after rounding accounting for any errors in dice roll results
        if sum(dice_nums) != result - modifier:
            i = result - modifier - sum(dice_nums)
            while True:
                for x in range(len(dice_nums)):
                    if i == 0:
                        break
                    elif i >= 1:
                        if dice_nums[x] < max_rolls[x]:
                            dice_nums[x] = dice_nums[x] + 1
                        else:
                            dice_nums[x] = max_rolls[x]
                        i -= 1
                    else:
                        if dice_nums[x] > roll_grouped[x][0]:
                            dice_nums[x] = dice_nums[x] - 1
                        else:
                            dice_nums[x] = roll_grouped[x][0]
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


if __name__ == '__main__':
    ReverseDice("6d20+5d10+5d4=60")
