"""
    Delta_function(x)

Implements an approximation of the Dirac delta function.
Returns a large value at x=0 and 0 elsewhere.

Properties:
- δ(x) = 0 for x ≠ 0
- δ(x) = ∞ for x = 0
- ∫δ(x)dx = 1
"""
function delta_function(x)
    # Using a very small epsilon for numerical approximation
    ε = 1e-100
    if abs(x) < ε
        return 1/ε
    else
        return 0.0
    end
end

"""
    delta_n_function(x, n)

Implements a parameterized version of the delta function approximation:
δₙ(x) = n if |x| < 1/(2n), 0 otherwise

As n approaches infinity, this approaches the true delta function.
"""
function delta_n_function(x, n)
    if abs(x) < 1/(2n)
        return n
    else
        return 0.0
    end
end

"""
    sifting_property(f, a, n=1000)

Demonstrates the sifting property of the delta function:
∫f(x)δ(x-a)dx = f(a)

Parameters:
- f: Function to be sampled
- a: Point at which to evaluate
- n: Parameter for delta function approximation
"""
function sifting_property(f, a, n=10000000)
    # Define integration limits around the point a
    dx = 1/(2n)
    x_range = range(a - 2dx, a + 2dx, length=1000)
    
    # Numerical integration using trapezoidal rule
    integral = 0.0
    for x in x_range[1:end-1]
        integral += f(x) * delta_n_function(x - a, n) * (x_range[2] - x_range[1])
    end
    
    return integral
end

"""
    sample_2d_image(image, sample_points)

Samples a 2D image at specified points using delta functions.

Parameters:
- image: 2D array representing the image
- sample_points: Array of (x,y) coordinates where to sample
"""
function sample_2d_image(image, sample_points)
    samples = []
    for (x, y) in sample_points
        # Convert to integer indices
        i, j = round.(Int, (x, y))
        if 1 <= i <= size(image, 1) && 1 <= j <= size(image, 2)
            push!(samples, image[i, j])
        end
    end
    return samples
end

;