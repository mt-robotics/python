# Convert a fractional number to float

```python
from fractions import Fraction

float_num = 0.1

fraction_num = Fraction(float_num)
```

Output is: 3602879701896397/36028797018963968

Why is it not 1/10 as we expect?
> Floating-point numbers are represented approximately in computers due to their binary nature. This can lead to small inaccuracies when converting floating-point numbers to fractions directly.

3602879701896397/36028797018963968 is definitely not wrong, yet it's very impractical. To get a more practical result, use the `.limit_denominator(<max_denominator>)` method of the `Fraction` class:

```python
fraction_num = Fraction(float_num).limit_denominator()
# default max_denominator is 1,000,000. The larger the max_denominator, the more accurate the result will be.
# max_denominator = 10 : Simplifies the fraction to a very basic level, useful for rough approximations
# max_denominator = 100 : Easier to work with and sufficient for many everyday calculations.
# max_denominator = 1000 : Provides a reasonable level of accuracy while keeping the fraction manageable and not overly complex.
# max_denominator = 10000 : Offers better precision while keeping the denominator within a practical range.
```

Now the output is 1/10.
