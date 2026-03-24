import os

class CoilParameters:
    def __init__(self, radius, turns, distance):
        self.radius = radius
        self.turns = turns
        self.distance = distance

    def validate(self):
        if self.radius <= 0 or self.turns <= 0 or self.distance <= 0:
            raise ValueError("Coil parameters must be positive.")

# Initialize arrays for segments
segments_fcu = []
segments_bcu = []
segments_all = []

# Function to add segments
def add_segments(segment_list, segment):
    segment_list.append(segment)

# Improved file creation and error handling
def create_file(filename):
    if os.path.exists(filename):
        print(f"Skipping creation of {filename}, file already exists.")
        return False
    # Implement actual file creation logic here
    return True

# Code for generating coils
try:
    # Example usage of adding segments
    add_segments(segments_fcu, ('F.Cu', 1, 2, 3))  # Sample segment for F.Cu
    add_segments(segments_bcu, ('B.Cu', 1, 2, 3))  # Sample segment for B.Cu
    # Ensure ordering is consistent
    segments_bcu.sort()  # Sort B.Cu segments for consistency

    # Populate all segments
    segments_all = segments_fcu + segments_bcu

except Exception as e:
    print(f"An error occurred: {e}")
