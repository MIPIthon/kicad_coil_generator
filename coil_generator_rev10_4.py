# **********************************************************************************
# Coil generator
# **********************************************************************************
# Revision: 10.4
# Date: 2026-03-24
# Author: MP
# **********************************************************************************
import math as m
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
from matplotlib.ticker import MultipleLocator

# **********************************************************************************
# Global variables 
# **********************************************************************************


# Used to store all traces on F.Cu for resistance calculation
segments_fcu = []

# Used to store all traces on B.Cu for resistance calculation
segments_bcu = []

# Used to store all traces on both copper layers for resistance calculation
segments_all = []


# Define the name of the footprint
fp_name = "_test"
file_ending_footprint = ".kicad_mod"
file_ending_config = ".json"
file_ending_plot = "pdf" # without dot!
header = '(footprint "'+fp_name+'"\n'

# Define track material properties and thickness
resistivity = 0.01721       # (copper) in Ohm*mm^2/m
trace_thickness = 0.035     # in mm
pcb_thickness = -1.58       # in mm (negative sign as it is assigned in the stack-up to B.Cu)


# **********************************************************************************
# Parameters
# **********************************************************************************
# ... for the via connection the layers
param_via_layer_conn = {
    'id_number': 3,             # id of via (or PTH)
    'typ': "circle",            # "roundrect" or "circle"
    'x': 0,                     # in mm (not used, determined by function)
    'y': 0,                     # in mm (not used, determined by function)
    'angle': 0,                 # in ° (not used)
    'drill_xo': 0,              # in mm (offset of the drill hole in x dir.) 
    'drill_yo': 0,              # in mm (offset of the drill hole in y dir.)
    'drill_dia': 0.45,          # in mm (used, final diameter of the PTH)
    'size_x' : 1,               # in mm (used, outer pad size in x dir.)
    'size_w': 1,                # in mm (used, drawing a spline between trace width and conn size)
    'size_y': 1,                # in mm (used, outer pad size in y dir.)
    'rratio': 0,                # range 0-1 equals to 0 to 100% (no effect)
}

# ... for the via connecting one side of the coil to the outside world
param_ext_conn_1 = {
    'id_number': 1,             # id of via (or PTH)
    'typ': "roundrect",         # "roundrect" or "circle"
    'x': 0,                     # in mm (not used, determined by function)
    'y': 0,                     # in mm (not used, determined by function)
    'angle': 0,                 # in ° (not used)
    'drill_xo': 0.9,            # in mm (offset of the drill hole in x dir.) 
    'drill_yo': 0,              # in mm (offset of the drill hole in y dir.)
    'drill_dia': 0.9,           # in mm (used, final diameter of the PTH)
    'size_x' : 3.6,             # in mm (used, outer pad size in x dir.) 
    'size_w': 1.8,              # in mm (used, drawing a spline between trace width and conn size)
    'size_y': 1.8,              # in mm (used, outer pad size in y dir.)
    'rratio': 0.5,              # range 0-1 equals to 0 to 100% (no effect)
}

# ... for the via connecting the other side of the coil to the outside world
param_ext_conn_2 = {
    'id_number': 2,             # id of via (or PTH)
    'typ': "roundrect",         # "roundrect" or "circle"
    'x': 0,                     # in mm (not used, determined by function)
    'y': 0,                     # in mm (not used, determined by function)
    'angle': 0,                 # in ° (not used)
    'drill_xo': -0.9,           # in mm (offset of the drill hole in x dir.) 
    'drill_yo': 0,              # in mm (offset of the drill hole in y dir.)
    'drill_dia': 0.9,           # in mm (used, final diameter of the PTH)
    'size_x' : 3.6,             # in mm (used, outer pad size in x dir.)
    'size_w': 1.8,              # in mm (used, drawing a spline between trace width and conn size)
    'size_y': 1.8,              # in mm (used, outer pad size in y dir.)
    'rratio': 0.5,              # range 0-1 equals to 0 to 100% (no effect)
}

# ... for the 2L coil system
param_2L_coil = {
    'x_c': 0,                   # in mm
    'y_c': 0,                   # in mm
    'w_in': 36.2,               # in mm
    'h_in': 41.2,               # in mm
    'n': 33,                    # number of windings per layer (no unit)
    'gap': 18,                  # in mm
    'gap_con': True,            # True or False 
    'gap_con_dir': 1,           # Direction of connection either -1 or 1
    'const_spacing': True,     # True or False
    'spacing': 0.35,            # in mm
    'const_r': False,            # True or False
    'rr': 0.331491712707182,    # range 0-1 equals to 0 to 100%
    'conn': "in",               # determines, where the connection to the outside world is located
                                # either "in" or "out", leave empty if not used
    'conn_pad_x_spacing': 10.16, # Spacing between both pads in x direction
    'conn_pad_y_spacing': 1.45, # Spacing between both pads and the coil in y direction
    'conn_via_y_spacing': 0.625,# via used to connect the different layers of the coil
    'conn_via_lay': param_via_layer_conn,
    'conn_via_ext_con_1': param_ext_conn_1,
    'conn_via_ext_con_2': param_ext_conn_2,
    'pcb_thickness': pcb_thickness,
    'seg': 28,                   # no unit
    'width': 0.2,               # in mm
    'Lint_uH': 0,               # in uH
    'Lext_uH': 0,               # in uH
    'Mtot_uH': 0,               # in uH
    'Ltot_uH': 0,               # in uH
    'R_ohm': 0,                 # in Ohm
    'trace_len_mm': 0,          # in mm
    'resistivity': resistivity, # (copper) in Ohm*mm^2/m
    'trace_thickness': trace_thickness, # in mm
}


# **********************************************************************************
# Create text on layer
# **********************************************************************************
def fct_fp_text(text_str, x, y, layer, size, thickness):
    out_str = '\t(fp_text user "'+text_str+'" '
    out_str += '(at '+str(x)+' '+str(y)+' '+'0) '
    out_str += '(layer "'+str(layer)+'"'+" knockout) "
    out_str += '(effects (font (size '+str(size)+' '+str(size)+') '
    out_str += '(thickness '+str(thickness)+')) '
    out_str += '(justify left)))\n'
    return out_str

# **********************************************************************************
# Function to draw a smd pad on a specific layer (used for traces)
# **********************************************************************************
def fct_pad(x, y, width, layer, id_):
    out_str = '\t(pad "'+str(id_)+'"'+" smd circle "
    out_str += "(at "+str(x)+" "+str(y)+" 1) " 
    out_str += "(size "+str(width)+" "+str(width)+") "
    out_str += '(layers "'+layer+'"))\n'
    return out_str

# **********************************************************************************
# Function to draw a via
# **********************************************************************************

def fct_via_p(p):
    # Supported types: "roundrect", "circle"
    out_str = '\t(pad "'+str(p['id_number'])+'" thru_hole '+str(p['typ'])+" "
    out_str += "(at "+str(p['x'])+" "+str(p['y'])+" "+str(p['angle'])+") "
    out_str += "(size "+str(p['size_x'])+" "+str(p['size_y'])+") "
    out_str += "(drill "+str(p['drill_dia'])
    if (p['typ'] == "roundrect"):
        out_str += "(offset "+str(p['drill_xo'])+" "+str(p['drill_yo'])+")) "
    else:
        out_str += ") "
    out_str += '(layers "*.Cu" "*.Mask") '
    out_str += '(solder_mask_margin 0) '
    out_str += '(clearance 0)'
    if (p['typ'] == "roundrect"):
        out_str += " (roundrect_rratio "+str(p['rratio'])+'))\n'
    else:
        out_str += ')\n'
    return out_str


# **********************************************************************************
# Function to draw a line on a specific layer
# **********************************************************************************

def fct_fp_line_len_res(xs, ys, xe, ye, width, layer):
    global segments_fcu
    global segments_bcu
    global point_array_fcu
    global point_array_bcu
    
    out_str = "\t(fp_line (start " +str(xs)+" "+str(ys)+") "
    out_str += "(end "+str(xe)+" "+str(ye)+") "
    out_str += "(stroke (width "+str(width)+") "
    out_str += "(type default)) "
    out_str += '(layer "'+layer+'"))\n'
    vect_len = m.sqrt((xe-xs)*(xe-xs)+(ye-ys)*(ye-ys))
    area_mm = width*trace_thickness
    resistance = resistivity*(1e-3*vect_len)/area_mm
    
    if layer == "F.Cu":
        segment_fcu = np.array([[xs*1E-3, ys*1E-3, 0], [xe*1E-3, ye*1E-3, 0]], dtype=float)
        segments_fcu.append(segment_fcu)
    if layer == "B.Cu":
        segment_bcu = np.array([[xe*1E-3, ye*1E-3, pcb_thickness*1E-3], [xs*1E-3, ys*1E-3, pcb_thickness*1E-3]], dtype=float)
        segments_bcu.append(segment_bcu)
    return out_str, vect_len, resistance

# **********************************************************************************
# Function to draw an arcsegment on a specific layer
# **********************************************************************************

def fct_draw_arc_seg_len_res(xc, yc, dia, alpha_s, alpha_e, seg, width, layer):
    pts = np.linspace(alpha_s, alpha_e, seg, endpoint=True)
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0
    for i in range(0, len(pts)-1):
        #print(str(pts[i])+" "+str(pts[i+1]))
        xs = (dia/2)*m.sin(pts[i]*m.pi/180)
        ys = (dia/2)*m.cos(pts[i]*m.pi/180)
        xe = (dia/2)*m.sin(pts[i+1]*m.pi/180)
        ye = (dia/2)*m.cos(pts[i+1]*m.pi/180)
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xc+xs, yc+ys, xc+xe, yc+ye, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
    return out_str, vect_len, resistance


# **********************************************************************************
# Function to draw variable width line (e.g. exponential) on a specific layer
# **********************************************************************************

def fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, layer, ws, we, id_):
    return fct_pad_exp_var_len_res_spline([xs, ys], [xm, ym], [xe, ye], ws, we, layer, id_)


def fct_pad_exp_var_len_res_spline(p0, p1, p2, ws, we, layer, id_):
    """
    p0, p1, p2 = (x, y) control points for spline
    ws, we = start and end widths
    """

    out_str = ""

    # Extract coordinates
    x = np.array([p0[0], p1[0], p2[0]])
    y = np.array([p0[1], p1[1], p2[1]])

    # Build cubic spline
    cs_x = CubicSpline([0, 0.5, 1], x)
    cs_y = CubicSpline([0, 0.5, 1], y)

    # Estimate curve length by oversampling
    t_dense = np.linspace(0, 1, 500)
    xd = cs_x(t_dense)
    yd = cs_y(t_dense)
    seg = np.sqrt(np.diff(xd)**2 + np.diff(yd)**2)
    vect_len = np.sum(seg)

    # Determine number of pads
    ratio = m.ceil(vect_len / (0.1 * min(ws, we)))

    # Sample spline at correct resolution
    t = np.linspace(0, 1, ratio + 1)
    x_arr = cs_x(t)
    y_arr = cs_y(t)

    # Nonlinear width sweep
    f = 1 / (t + 0.3)
    f_norm = (f - f[0]) / (f[-1] - f[0])

    w_max = max(ws, we)
    w_min = min(ws, we)

    w_sweep = w_max - (w_max - w_min) * f_norm

    if ws > we:
        w_arr = w_sweep
    else:
        w_arr = w_sweep[::-1]

    # Generate pads
    for i in range(len(x_arr)):
        out_str += fct_pad(x_arr[i], y_arr[i], w_arr[i], layer, id_)

    # Resistance approximation
    area_mm = ((w_min + w_max) / 2) *trace_thickness
    resistance = resistivity * (1e-3 * vect_len) / area_mm

    return out_str, vect_len, resistance


# **********************************************************************************
# Coil generation function
# **********************************************************************************

def fct_roundrect_gapped_p_len_res(x_c, y_c, w, h, rr, seg, width, gap, gap_con, gap_con_dir, spacing, layer, header_on):
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0

    if True == header_on:
        out_str = header
    
    # rr can be in the range of 0 to 1 (0 - 100%) relative to smallest side
    # Determine the smallest side of the rectangle
    if (w <= h):
        dia = rr*abs(w)
    else:
        dia = rr*abs(h)

    # Only for debugging purposes print calculated radius
    #print("Radius = "+str(dia/2))
    
    
    if gap_con_dir > 0:
        # *** F.Cu
        # Draw the two lines around the gap
        # Right gap side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+gap/2, y_c+h/2, x_c+(w-dia)/2, y_c+h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Upper right corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c+(w-dia)/2, y_c+(h-dia)/2, dia, 0, 90, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw for lines for all sides
        # Right side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+w/2, y_c+(h-dia)/2, x_c+w/2, y_c-(h-dia)/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Lower right corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c+(w-dia)/2, y_c-(h-dia)/2, dia, 90, 180, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw for lines for all sides
        # Bottom side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+(w-dia)/2, y_c-h/2, x_c-(w-dia)/2, y_c-h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Lower left corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c-(w-dia)/2, y_c-(h-dia)/2, dia, 180, 270, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw for lines for all sides
        # Left side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-w/2, y_c-(h-dia)/2, x_c-w/2, y_c+(h-dia)/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        
        # Draw four arc segments for all edges
        # Upper left corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c-(w-dia)/2, y_c+(h-dia)/2, dia, 270, 360, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw the two lines around the gap
        # Left gap side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-(w-dia)/2, y_c+h/2, x_c-gap/2, y_c+h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance

        #If activate, draw a connection to the next winding
        if True == gap_con:
            temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-gap/2, y_c+h/2, x_c+gap/2, y_c+h/2+spacing, width, layer)
            out_str += temp_str
            vect_len += temp_len
            resistance += temp_resistance
    else:
        # *** B.Cu
        
        # Draw the two lines around the gap
        # Left gap side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-(w-dia)/2, y_c+h/2, x_c-gap/2, y_c+h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Upper left corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c-(w-dia)/2, y_c+(h-dia)/2, dia, 270, 360, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw for lines for all sides
        # Left side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-w/2, y_c-(h-dia)/2, x_c-w/2, y_c+(h-dia)/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Lower left corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c-(w-dia)/2, y_c-(h-dia)/2, dia, 180, 270, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw for lines for all sides
        # Bottom side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+(w-dia)/2, y_c-h/2, x_c-(w-dia)/2, y_c-h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Lower right corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c+(w-dia)/2, y_c-(h-dia)/2, dia, 90, 180, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw for lines for all sides
        # Right side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+w/2, y_c+(h-dia)/2, x_c+w/2, y_c-(h-dia)/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw four arc segments for all edges
        # Upper right corner
        temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c+(w-dia)/2, y_c+(h-dia)/2, dia, 0, 90, seg, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Draw the two lines around the gap
        # Right gap side
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+gap/2, y_c+h/2, x_c+(w-dia)/2, y_c+h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        #If activate, draw a connection to the next winding
        if True == gap_con:
            temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-gap/2, y_c+h/2+spacing, x_c+gap/2, y_c+h/2, width, layer)
            out_str += temp_str
            vect_len += temp_len
            resistance += temp_resistance


    if True == header_on:
        out_str += ")"
        
    return out_str, vect_len, resistance


def fct_round_gapped_rect_coil_p_len_res(p, gap_con_dir, layer, header_on):
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0
    
    if True == header_on:
        out_str = header

    # w_in = inner width of the coil
    # h_in = inner height of the coil
    # n = number of windings (loops)
    # gap = size of the gap
    # const_spacing: if true, the arcsegments do have an equal spacing between each other 
    # spacing = spacing between adjacent traces
    # const_r: If true, corner radius is equal for all n loops. Otherwise individually calculated for each loop via rr.
    # rr = radius ratio (how much rounding of the edges relative to the width or height) 
    # seg = number of lines used to draw arc segment
    # width = trace width
    # layer = specified layer for drawing the coil
    
    for i in range(0, p['n']):
        w = p['w_in']+i*2*p['spacing']
        h = p['h_in']+i*2*p['spacing']

        if (p['const_spacing'] == False) and (p['const_r'] == False):
            calc_rr = p['rr'] # use constant radius ratio mode
        if (p['const_spacing'] == False) and (p['const_r'] == True):
            if (w <= h): # use constant radius mode
                calc_rr = (p['w_in']/w)*p['rr']
            else:
                calc_rr = (p['h_in']/h)*p['rr']
        if (p['const_spacing'] == True) and (p['const_r'] == False):
            if (w <= h): # use constant spacing mode
                calc_rr = p['rr']*(p['w_in']/w)+i*2*p['spacing']/w
            else:
                calc_rr = p['rr']*(p['h_in']/h)+i*2*p['spacing']/h
        if (p['const_spacing'] == True) and (p['const_r'] == True):
            calc_rr = p['rr'] # use constant radius ratio mode
        
        # Only for debugging:
        #print("Calc rr: "+str(calc_rr))
        if (calc_rr > 1):
            print("Error in input definition rr > 1")
            break
    
        temp_str, temp_len, temp_resistance = fct_roundrect_gapped_p_len_res(p['x_c'], p['y_c'], w, h, calc_rr, p['seg'], p['width'], p['gap'], i<(p['n']-1), gap_con_dir, p['spacing'], layer, False)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
    
    if True == header_on:
        out_str += ")"
    return out_str, vect_len, resistance



def fct_create_2L_rounded_rect_coil_p_len_res_conn(p, header_on):
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0
    
    xm_pad_coeff = 2.6
    ym_pad_coeff = 3
    
    xm_via_coeff = 3.6
    ym_via_coeff = 3
    
    if True == header_on:
        out_str = header

    # Draw on F.Cu layer
    temp_str, temp_len, temp_resistance = fct_round_gapped_rect_coil_p_len_res(p, 1, "F.Cu", False)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance
    
    # Draw on B.Cu layer    
    temp_str, temp_len, temp_resistance = fct_round_gapped_rect_coil_p_len_res(p, -1, "B.Cu", False)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance
    
    if p['conn'] == "in": # external connection inside of coil body
        # Create pad 1
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+p['h_in']/2
        
        xm = p['x_c']-p['gap']/xm_pad_coeff
        ym = p['y_c']-p['conn_pad_y_spacing']/ym_pad_coeff+p['h_in']/2

        xe = p['x_c']-p['conn_pad_x_spacing']/2
        ye = p['y_c']-p['conn_pad_y_spacing']+p['h_in']/2
        
        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "B.Cu", p['width'], p['conn_via_ext_con_1']['size_w'], p['conn_via_ext_con_1']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        p['conn_via_ext_con_1']["x"] = xe
        p['conn_via_ext_con_1']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_1'])
        
        # Create pad 2
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+p['h_in']/2
        
        xm = p['x_c']+p['gap']/xm_pad_coeff
        ym = p['y_c']-p['conn_pad_y_spacing']/ym_pad_coeff+p['h_in']/2
        
        xe = p['x_c']+p['conn_pad_x_spacing']/2
        ye = p['y_c']-p['conn_pad_y_spacing']+p['h_in']/2

        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "F.Cu", p['width'], p['conn_via_ext_con_2']['size_w'], p['conn_via_ext_con_2']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        p['conn_via_ext_con_2']["x"] = xe
        p['conn_via_ext_con_2']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_2'])
        
        # Create via    
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        
        xm = p['x_c']+p['gap']/xm_via_coeff
        ym = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_via_y_spacing']/ym_via_coeff
        
        xe = p['x_c']
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "B.Cu", p['width'], p['conn_via_lay']['size_w'], p['conn_via_lay']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        
        xm = p['x_c']-p['gap']/xm_via_coeff
        ym = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_via_y_spacing']/ym_via_coeff
        
        xe = p['x_c']
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "F.Cu", p['width'], p['conn_via_lay']['size_w'], p['conn_via_lay']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create via for layer connection
        p['conn_via_lay']["x"] = xe
        p['conn_via_lay']["y"] = ye
        out_str += fct_via_p(p['conn_via_lay'])
        
    elif p['conn'] == "out": # external connection outside of the coil body
        # Create pad 1
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        
        xm = p['x_c']-p['gap']/xm_pad_coeff
        ym = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_pad_y_spacing']/ym_pad_coeff
        
        xe = p['x_c']-p['conn_pad_x_spacing']/2
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['conn_pad_y_spacing']+p['h_in']/2
        
        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "F.Cu", p['width'], p['conn_via_ext_con_1']['size_w'], p['conn_via_ext_con_1']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        p['conn_via_ext_con_1']["x"] = xe
        p['conn_via_ext_con_1']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_1'])
        
        # Create pad 2
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        
        xm = p['x_c']+p['gap']/xm_pad_coeff
        ym = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_pad_y_spacing']/ym_pad_coeff
        
        xe = p['x_c']+p['conn_pad_x_spacing']/2
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['conn_pad_y_spacing']+p['h_in']/2

        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "B.Cu", p['width'], p['conn_via_ext_con_2']['size_w'],p['conn_via_ext_con_2']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        p['conn_via_ext_con_2']["x"] = xe
        p['conn_via_ext_con_2']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_2'])
        
        # Create via
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+p['h_in']/2
        
        xm = p['x_c']-p['gap']/xm_via_coeff
        ym = p['y_c']+p['h_in']/2-p['conn_via_y_spacing']/ym_via_coeff
        
        xe = p['x_c']
        ye = p['y_c']+p['h_in']/2-p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "B.Cu", p['width'], p['conn_via_lay']['size_w'], p['conn_via_lay']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+p['h_in']/2
        
        xm = p['x_c']+p['gap']/xm_via_coeff
        ym = p['y_c']+p['h_in']/2-p['conn_via_y_spacing']/ym_via_coeff
        
        xe = p['x_c']
        ye = p['y_c']+p['h_in']/2-p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_pad_exp_var_spline_wrapper(xs, ys, xm, ym, xe, ye, "F.Cu", p['width'], p['conn_via_lay']['size_w'], p['conn_via_lay']['id_number'])
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create via for layer connection
        p['conn_via_lay']["x"] = xe
        p['conn_via_lay']["y"] = ye
        out_str += fct_via_p(p['conn_via_lay'])
    else:
        print("No definition for external connection.") # do nothing


    out_str += fct_fp_text("${Part number}", 0, 0, "F.SilkS", 1.5, 0.1875)
    out_str += fct_fp_text("${Revision}", 0, 0, "F.SilkS", 1.5, 0.1875)
    
    if True == header_on:
        out_str += ")"
    return out_str, vect_len, resistance

# **********************************************************************************
# Main function
# **********************************************************************************

if __name__ == "__main__":
        
    out, len_, res = fct_create_2L_rounded_rect_coil_p_len_res_conn(param_2L_coil, True)
    
    
    plot_ticks = 5  # mm
    
    # ---------------------------------------------------------
    # FIGURE 1 — 2D TOP-DOWN VIEWS
    # ---------------------------------------------------------
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    
    # --- F.Cu (2D) ---
    axes[0].set_title("PCB Coil Geometry – F.Cu")
    axes[0].set_xlabel("x [mm]")
    axes[0].set_ylabel("y [mm]")
    axes[0].set_aspect("equal", "box")
    
    for seg in segments_fcu:
        p0 = seg[0] * 1e3   # convert to mm
        p1 = seg[1] * 1e3
        axes[0].plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            color="red",
            linewidth=1
        )
    
    axes[0].xaxis.set_major_locator(MultipleLocator(plot_ticks))
    axes[0].yaxis.set_major_locator(MultipleLocator(plot_ticks))
    axes[0].grid(True)
    
    # --- B.Cu (2D) ---
    axes[1].set_title("PCB Coil Geometry – B.Cu")
    axes[1].set_xlabel("x [mm]")
    axes[1].set_ylabel("y [mm]")
    axes[1].set_aspect("equal", "box")
    
    for seg in segments_bcu:
        p0 = seg[0] * 1e3
        p1 = seg[1] * 1e3
        axes[1].plot(
            [p0[0], p1[0]],
            [p0[1], p1[1]],
            color="blue",
            linewidth=1
        )
    
    axes[1].xaxis.set_major_locator(MultipleLocator(plot_ticks))
    axes[1].yaxis.set_major_locator(MultipleLocator(plot_ticks))
    axes[1].grid(True)

    file_name_2D_plot = fp_name+"_2D"+"."+file_ending_plot
    try:
        with open(file_name_2D_plot, "x") as f:
            print('File "'+file_name_2D_plot+'" created!')
            # Now save the figure
            plt.savefig(file_name_2D_plot, format=file_ending_plot)
    
    except FileExistsError:
        print('File "'+file_name_2D_plot+'" already exists!')

        
    plt.show()
    plt.close(fig)

        
    # ---------------------------------------------------------
    # FIGURE 2 — 3D SEGMENT VIEW
    # ---------------------------------------------------------
    fig3 = plt.figure(figsize=(10, 10))
    ax3 = fig3.add_subplot(111, projection="3d")
    
    ax3.set_title("3D PCB Coil Geometry (Segment View)")
    ax3.set_xlabel("x [mm]")
    ax3.set_ylabel("y [mm]")
    ax3.set_zlabel("z [mm]")
    
    # --- F.Cu segments (red) ---
    for seg in segments_fcu:
        p0 = seg[0] * 1e3   # convert to mm
        p1 = seg[1] * 1e3
        ax3.plot([p0[0], p1[0]],
                 [p0[1], p1[1]],
                 [p0[2], p1[2]],
                 color="red", linewidth=0.5)
    
    # --- B.Cu segments (blue) ---
    for seg in segments_bcu:
        p0 = seg[0] * 1e3
        p1 = seg[1] * 1e3
        ax3.plot([p0[0], p1[0]],
                 [p0[1], p1[1]],
                 [p0[2], p1[2]],
                 color="blue", linewidth=0.5)
    
    ax3.view_init(elev=30, azim=65)
    plt.tight_layout()
  
    file_name_3D_plot = fp_name+"_3D"+"."+file_ending_plot
    try:
        with open(file_name_3D_plot, "x") as f:
            print('File "'+file_name_3D_plot+'" created!')
            # Now save the figure
            plt.savefig(file_name_3D_plot, format=file_ending_plot)
    
    except FileExistsError:
        print('File "'+file_name_3D_plot+'" already exists!')

    plt.show()
    plt.close(fig3)

    
    print("Length of total coil winding [mm]: "+str(len_))
    print("Estimated resistance of coil winding [Ohm]: "+str(res))
    
    param_2L_coil['R_ohm'] = res
    param_2L_coil['trace_len_mm'] = len_

    json_str = json.dumps(param_2L_coil, indent=4)
    print(json_str)


    # Create footprint file
    try:
        with open(fp_name+file_ending_footprint, "x", encoding="utf-8") as f:
            print('File "'+fp_name+file_ending_footprint+'" created!')
            f.writelines(out)
    except FileExistsError:
        print('File "'+fp_name+file_ending_footprint+'" already exists!')

    # Create config file
    try:
        with open(fp_name+file_ending_config, "x") as f:
            print('File "'+fp_name+file_ending_config+'" created!')
            json.dump(param_2L_coil, f, indent=4)
    except FileExistsError:
        print('File "'+fp_name+file_ending_config+'" already exists!')
        

