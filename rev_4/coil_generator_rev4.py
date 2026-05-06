# **********************************************************************************
# Coil generator
# **********************************************************************************
# Revision: 4
# Date: 2025-12-08
# Author: MP
# **********************************************************************************
import numpy as np
import math as m
import copy

# **********************************************************************************
# Global variables 
# **********************************************************************************

# Define the name of the footprint
fp_name = "2L_coil_matrix_4x4"
file_ending = ".kicad_mod"
header = "(footprint "+fp_name+"\n"

# Define track material properties and thickness
resistivity = 0.01721       # (copper) in Ohm*mm^2/m
thickness = 0.035           # in mm

# **********************************************************************************
# Parameters
# **********************************************************************************
# ... for the via connection the layers
param_via_layer_conn = {
    'id_number': '',             # id of via (or PTH)
    'typ': "circle",            # "roundrect" or "circle"
    'x': 0,                     # in mm (not used, determined by function)
    'y': 0,                     # in mm (not used, determined by function)
    'angle': 0,                 # in ° (not used)
    'drill_xo': 0,              # in mm (offset of the drill hole in x dir.) 
    'drill_yo': 0,              # in mm (offset of the drill hole in y dir.)
    'drill_dia': 0.3,           # in mm (used, final diameter of the PTH)
    'size_x' : 0.6,             # in mm (used, outer pad size in x dir.) 
    'size_y': 0.6,              # in mm (used, outer pad size in y dir.)
    'rratio': 0,                # range 0-1 equals to 0 to 100% (no effect)
}

# ... for the via connecting one side of the coil to the outside world
param_ext_conn_1 = {
    'id_number': 1,             # id of via (or PTH)
    'typ': "circle",            # "roundrect" or "circle"
    'x': 0,                     # in mm (not used, determined by function)
    'y': 0,                     # in mm (not used, determined by function)
    'angle': 0,                 # in ° (not used)
    'drill_xo': 0,              # in mm (offset of the drill hole in x dir.) 
    'drill_yo': 0,              # in mm (offset of the drill hole in y dir.)
    'drill_dia': 0.5,           # in mm (used, final diameter of the PTH)
    'size_x' :1.2,             # in mm (used, outer pad size in x dir.) 
    'size_y': 1.2,              # in mm (used, outer pad size in y dir.)
    'rratio': 0,                # range 0-1 equals to 0 to 100% (no effect)
}

# ... for the via connecting the other side of the coil to the outside world
param_ext_conn_2 = {
    'id_number': 2,             # id of via (or PTH)
    'typ': "circle",            # "roundrect" or "circle"
    'x': 0,                     # in mm (not used, determined by function)
    'y': 0,                     # in mm (not used, determined by function)
    'angle': 0,                 # in ° (not used)
    'drill_xo': 0,              # in mm (offset of the drill hole in x dir.) 
    'drill_yo': 0,              # in mm (offset of the drill hole in y dir.)
    'drill_dia': 0.5,           # in mm (used, final diameter of the PTH)
    'size_x' : 1.2,             # in mm (used, outer pad size in x dir.) 
    'size_y': 1.2,              # in mm (used, outer pad size in y dir.)
    'rratio': 0,                # range 0-1 equals to 0 to 100% (no effect)
}

# ... for the 2L coil system
param_2L_coil = {
    'x_c': 0,                   # in mm
    'y_c': 0,                   # in mm
    'w_in': 12,                  # in mm
    'h_in': 6,                  # in mm
    'n': 16,                    # number of windings per layer (no unit)
    'gap': 6,                   # in mm
    'gap_con': True,            # True or False 
    'gap_con_dir': 1,           # Direction of connection either -1 or 1
    'const_spacing': False,     # True or False
    'spacing': 0.4,             # in mm
    'const_r': True,            # True or False
    'rr': 0.1,                  # range 0-1 equals to 0 to 100%
    'conn': "out",               # determines, where the connection to the outside world is located
                                # either "in" or "out", leave empty if not used
    'conn_pad_x_spacing': 2,  # Spacing between both pads in x direction
    'conn_pad_y_spacing': 1,  # Spacing between both pads and the coil in y direction
    'conn_via_y_spacing': 0.4,    # via used to connect the different layers of the coil
    'conn_via_lay': param_via_layer_conn,
    'conn_via_ext_con_1': param_ext_conn_1,
    'conn_via_ext_con_2': param_ext_conn_2,
    'seg': 28,                  # no unit
    'width': 0.2,               # in mm
}

# **********************************************************************************
# Function to draw a line on a specific layer
# **********************************************************************************
def fct_fp_line(xs, ys, xe, ye, width, layer):
    out_str = "\t(fp_line (start " +str(xs)+" "+str(ys)+") "
    out_str += "(end "+str(xe)+" "+str(ye)+") "
    out_str += "(stroke (width "+str(width)+") "
    out_str += "(type default)) "
    out_str += '(layer "'+layer+'"))\n'
    return out_str

def fct_fp_line_len(xs, ys, xe, ye, width, layer):
    out_str = "\t(fp_line (start " +str(xs)+" "+str(ys)+") "
    out_str += "(end "+str(xe)+" "+str(ye)+") "
    out_str += "(stroke (width "+str(width)+") "
    out_str += "(type default)) "
    out_str += '(layer "'+layer+'"))\n'
    vect_len = m.sqrt((xe-xs)*(xe-xs)+(ye-ys)*(ye-ys))
    return out_str, vect_len

def fct_fp_line_len_res(xs, ys, xe, ye, width, layer):
    out_str = "\t(fp_line (start " +str(xs)+" "+str(ys)+") "
    out_str += "(end "+str(xe)+" "+str(ye)+") "
    out_str += "(stroke (width "+str(width)+") "
    out_str += "(type default)) "
    out_str += '(layer "'+layer+'"))\n'
    vect_len = m.sqrt((xe-xs)*(xe-xs)+(ye-ys)*(ye-ys))
    area_mm = width*thickness
    resistance = resistivity*(1e-3*vect_len)/area_mm
    return out_str, vect_len, resistance

# **********************************************************************************
# Function to draw a circle on a specific layer
# **********************************************************************************
def fct_draw_circle(xc, yc, dia, seg, width, layer):
    pts = np.linspace(0, 360, seg, endpoint=True)
    out_str = ""
    for i in range(0, len(pts)-1):
        # print(str(pts[i])+" "+str(pts[i+1]))
        xs = (dia/2)*m.sin(pts[i]*m.pi/180)
        ys = (dia/2)*m.cos(pts[i]*m.pi/180)
        xe = (dia/2)*m.sin(pts[i+1]*m.pi/180)
        ye = (dia/2)*m.cos(pts[i+1]*m.pi/180)
        out_str += fct_fp_line(xc+xs, yc+ys, xc+xe, yc+ye, width, layer)
    return out_str

def fct_draw_circle_len(xc, yc, dia, seg, width, layer):
    pts = np.linspace(0, 360, seg, endpoint=True)
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    for i in range(0, len(pts)-1):
        # print(str(pts[i])+" "+str(pts[i+1]))
        xs = (dia/2)*m.sin(pts[i]*m.pi/180)
        ys = (dia/2)*m.cos(pts[i]*m.pi/180)
        xe = (dia/2)*m.sin(pts[i+1]*m.pi/180)
        ye = (dia/2)*m.cos(pts[i+1]*m.pi/180)
        temp_str, temp_len = fct_fp_line_len(xc+xs, yc+ys, xc+xe, yc+ye, width, layer)
        out_str += temp_str
        vect_len += temp_len
    return out_str, vect_len

def fct_draw_circle_len_res(xc, yc, dia, seg, width, layer):
    pts = np.linspace(0, 360, seg, endpoint=True)
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0
    for i in range(0, len(pts)-1):
        # print(str(pts[i])+" "+str(pts[i+1]))
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
# Function to draw an arcsegement on a specific layer
# **********************************************************************************
def fct_draw_arc_seg(xc, yc, dia, alpha_s, alpha_e, seg, width, layer):
    pts = np.linspace(alpha_s, alpha_e, seg, endpoint=True)
    out_str = ""
    for i in range(0, len(pts)-1):
        #print(str(pts[i])+" "+str(pts[i+1]))
        xs = (dia/2)*m.sin(pts[i]*m.pi/180)
        ys = (dia/2)*m.cos(pts[i]*m.pi/180)
        xe = (dia/2)*m.sin(pts[i+1]*m.pi/180)
        ye = (dia/2)*m.cos(pts[i+1]*m.pi/180)
        out_str += fct_fp_line(xc+xs, yc+ys, xc+xe, yc+ye, width, layer)
    return out_str

def fct_draw_arc_seg_len(xc, yc, dia, alpha_s, alpha_e, seg, width, layer):
    pts = np.linspace(alpha_s, alpha_e, seg, endpoint=True)
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    for i in range(0, len(pts)-1):
        #print(str(pts[i])+" "+str(pts[i+1]))
        xs = (dia/2)*m.sin(pts[i]*m.pi/180)
        ys = (dia/2)*m.cos(pts[i]*m.pi/180)
        xe = (dia/2)*m.sin(pts[i+1]*m.pi/180)
        ye = (dia/2)*m.cos(pts[i+1]*m.pi/180)
        temp_str, temp_len = fct_fp_line_len(xc+xs, yc+ys, xc+xe, yc+ye, width, layer)
        out_str += temp_str
        vect_len += temp_len
    return out_str, vect_len

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
# Function to draw a via
# **********************************************************************************
def fct_via(id_number, typ, x, y, angle, drill_xo, drill_yo, drill_dia, size_x, size_y, rratio):
    # Supported types: "roundrect", "circle"
    out_str = '\t(pad "'+str(id_number)+'" thru_hole '+str(typ)+" "
    out_str += "(at "+str(x)+" "+str(y)+" "+str(angle)+") "
    out_str += "(size "+str(size_x)+" "+str(size_y)+") "
    out_str += "(drill "+str(drill_dia)+" (offset "+str(drill_xo)+" "+str(drill_yo)+")) "
    out_str += '(layers "*.Cu" "*.Mask")'
    if (typ == "roundrect"):
        out_str += " (roundrect_rratio "+str(rratio)+'))\n'
    else:
        out_str += ')\n'
    return out_str

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
# Function to draw a rectangle shaped loop with rounded edges on a specific layer
# **********************************************************************************
def fct_roundrect(w, h, rr, seg, width, layer, header_on):
    out_str = ""
    if True == header_on:
        out_str = header
    
    # rr can be in the range of 0 to 1 (0 - 100%) relative to smallest side
    # Determine the smallest side of the rectangle
    if (w <= h):
        dia = rr*abs(w)
    else:
        dia = rr*abs(h)

    # Only for debugging purposes print calculated radius
    print("Radius = "+str(dia/2))
    
    out_str += fct_draw_arc_seg(-(w-dia)/2, (h-dia)/2, dia, 270, 360, seg, width, layer)
    out_str += fct_draw_arc_seg(-(w-dia)/2, -(h-dia)/2, dia, 180, 270, seg, width, layer)
    out_str += fct_draw_arc_seg((w-dia)/2, -(h-dia)/2, dia, 90, 180, seg, width, layer)
    out_str += fct_draw_arc_seg((w-dia)/2, (h-dia)/2, dia, 0, 90, seg, width, layer)

    out_str += fct_fp_line(w/2, (h-dia)/2, w/2, -(h-dia)/2, width, layer)
    out_str += fct_fp_line((w-dia)/2, -h/2, -(w-dia)/2, -h/2, width, layer)
    out_str += fct_fp_line(-w/2, (h-dia)/2, -w/2, -(h-dia)/2, width, layer)
    out_str += fct_fp_line((w-dia)/2, h/2, -(w-dia)/2, h/2, width, layer)

    if True == header_on:
        out_str += ")"
    return out_str

# **********************************************************************************
# Function to draw a single layer coil with a defined gap
# **********************************************************************************
def fct_roundrect_gapped(w, h, rr, seg, width, gap, gap_con, gap_con_dir, spacing, layer, header_on):
    out_str = ""
    if True == header_on:
        out_str = header
    
    # rr can be in the range of 0 to 1 (0 - 100%) relative to smallest side
    # Determine the smallest side of the rectangle
    if (w <= h):
        dia = rr*abs(w)
    else:
        dia = rr*abs(h)

    # Only for debugging purposes print calculated radius
    print("Radius = "+str(dia/2))

    # Draw four arc segments for all edges
    out_str += fct_draw_arc_seg(-(w-dia)/2, (h-dia)/2, dia, 270, 360, seg, width, layer)
    out_str += fct_draw_arc_seg(-(w-dia)/2, -(h-dia)/2, dia, 180, 270, seg, width, layer)
    out_str += fct_draw_arc_seg((w-dia)/2, -(h-dia)/2, dia, 90, 180, seg, width, layer)
    out_str += fct_draw_arc_seg((w-dia)/2, (h-dia)/2, dia, 0, 90, seg, width, layer)

    # Draw for lines for all sides
    out_str += fct_fp_line(w/2, (h-dia)/2, w/2, -(h-dia)/2, width, layer)
    out_str += fct_fp_line((w-dia)/2, -h/2, -(w-dia)/2, -h/2, width, layer)
    out_str += fct_fp_line(-w/2, (h-dia)/2, -w/2, -(h-dia)/2, width, layer)

    # Draw the two lines around the gap
    out_str += fct_fp_line((w-dia)/2, h/2, gap/2, h/2, width, layer)
    out_str += fct_fp_line(-(w-dia)/2, h/2, -gap/2, h/2, width, layer)
    
    # If activate, draw a connection to the next winding
    if True == gap_con:
        if gap_con_dir > 0:
            out_str += fct_fp_line(-gap/2, h/2, gap/2, h/2+spacing, width, layer)
        else:
            out_str += fct_fp_line(-gap/2, h/2+spacing, gap/2, h/2, width, layer)
    
    if True == header_on:
        out_str += ")"
    return out_str

def fct_roundrect_gapped_p(x_c, y_c, w, h, rr, seg, width, gap, gap_con, gap_con_dir, spacing, layer, header_on):
    out_str = ""
    if True == header_on:
        out_str = header
    
    # rr can be in the range of 0 to 1 (0 - 100%) relative to smallest side
    # Determine the smallest side of the rectangle
    if (w <= h):
        dia = rr*abs(w)
    else:
        dia = rr*abs(h)

    # Only for debugging purposes print calculated radius
    print("Radius = "+str(dia/2))

    # Draw four arc segments for all edges
    out_str += fct_draw_arc_seg(x_c-(w-dia)/2, y_c+(h-dia)/2, dia, 270, 360, seg, width, layer)
    out_str += fct_draw_arc_seg(x_c-(w-dia)/2, y_c-(h-dia)/2, dia, 180, 270, seg, width, layer)
    out_str += fct_draw_arc_seg(x_c+(w-dia)/2, y_c-(h-dia)/2, dia, 90, 180, seg, width, layer)
    out_str += fct_draw_arc_seg(x_c+(w-dia)/2, y_c+(h-dia)/2, dia, 0, 90, seg, width, layer)

    # Draw for lines for all sides
    out_str += fct_fp_line(x_c+w/2, y_c+(h-dia)/2, x_c+w/2, y_c-(h-dia)/2, width, layer)
    out_str += fct_fp_line(x_c+(w-dia)/2, y_c-h/2, x_c-(w-dia)/2, y_c-h/2, width, layer)
    out_str += fct_fp_line(x_c-w/2, y_c+(h-dia)/2, x_c-w/2, y_c-(h-dia)/2, width, layer)

    # Draw the two lines around the gap
    out_str += fct_fp_line(x_c+(w-dia)/2, y_c+h/2, x_c+gap/2, y_c+h/2, width, layer)
    out_str += fct_fp_line(x_c-(w-dia)/2, y_c+h/2, x_c-gap/2, y_c+h/2, width, layer)
    
    # If activate, draw a connection to the next winding
    if True == gap_con:
        if gap_con_dir > 0:
            out_str += fct_fp_line(x_c-gap/2, y_c+h/2, x_c+gap/2, y_c+h/2+spacing, width, layer)
        else:
            out_str += fct_fp_line(x_c-gap/2, y_c+h/2+spacing, x_c+gap/2, y_c+h/2, width, layer)
    
    if True == header_on:
        out_str += ")"
    return out_str

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

    # Draw four arc segments for all edges
    temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c-(w-dia)/2, y_c+(h-dia)/2, dia, 270, 360, seg, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance

    temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c-(w-dia)/2, y_c-(h-dia)/2, dia, 180, 270, seg, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance

    temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c+(w-dia)/2, y_c-(h-dia)/2, dia, 90, 180, seg, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance

    temp_str, temp_len, temp_resistance = fct_draw_arc_seg_len_res(x_c+(w-dia)/2, y_c+(h-dia)/2, dia, 0, 90, seg, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance
    
    # Draw for lines for all sides
    temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+w/2, y_c+(h-dia)/2, x_c+w/2, y_c-(h-dia)/2, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance
    
    temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+(w-dia)/2, y_c-h/2, x_c-(w-dia)/2, y_c-h/2, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance

    temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-w/2, y_c+(h-dia)/2, x_c-w/2, y_c-(h-dia)/2, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance

    # Draw the two lines around the gap
    temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c+(w-dia)/2, y_c+h/2, x_c+gap/2, y_c+h/2, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance

    temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-(w-dia)/2, y_c+h/2, x_c-gap/2, y_c+h/2, width, layer)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance
    
    # If activate, draw a connection to the next winding
    if True == gap_con:
        if gap_con_dir > 0:
            temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-gap/2, y_c+h/2, x_c+gap/2, y_c+h/2+spacing, width, layer)
        else:
            temp_str, temp_len, temp_resistance = fct_fp_line_len_res(x_c-gap/2, y_c+h/2+spacing, x_c+gap/2, y_c+h/2, width, layer)
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance

    if True == header_on:
        out_str += ")"
        
    return out_str, vect_len, resistance

# **********************************************************************************
# Function to draw multiple rectangle shaped loops on a specific layer
# **********************************************************************************
def fct_round_rect_coil(w_in, h_in, n, spacing, rr, seg, width, layer):
    out_str = ""
    out_str = header
    for i in range(0, n):
        w = w_in+i*2*spacing
        h = h_in+i*2*spacing
        out_str += fct_roundrect(w, h, rr, seg, width, layer, False)
    out_str += ")"
    return out_str

# **********************************************************************************
# Function to draw multiple gapped rectangle shaped loops on a specific layer
# **********************************************************************************
def fct_round_gapped_rect_coil(w_in, h_in, n, gap, gap_con_dir, const_spacing, spacing, const_r, rr, seg, width, layer, header_on):
    out_str = ""
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
    
    for i in range(0, n):
        w = w_in+i*2*spacing
        h = h_in+i*2*spacing

        if (const_spacing == False) and (const_r == False):
            calc_rr = rr # use constant radius ratio mode
        if (const_spacing == False) and (const_r == True):
            if (w <= h): # use constant radius mode
                calc_rr = (w_in/w)*rr
            else:
                calc_rr = (h_in/h)*rr
        if (const_spacing == True) and (const_r == False):
            if (w <= h): # use constant spacing mode
                calc_rr = rr*(w_in/w)+i*2*spacing/w
            else:
                calc_rr = rr*(h_in/h)+i*2*spacing/h
        if (const_spacing == True) and (const_r == True):
            calc_rr == rr # use constant radius ratio mode
        
        # Only for debugging
        #print("Calc rr: "+str(calc_rr))
        if (calc_rr > 1):
            print("Error in input definition rr > 1")
            break
        
        out_str += fct_roundrect_gapped(w, h, calc_rr, seg, width, gap, i<(n-1), gap_con_dir, spacing, layer, False)

    if True == header_on:
        out_str += ")"
    return out_str

def fct_round_gapped_rect_coil_p(p, gap_con_dir, layer, header_on):
    out_str = ""
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
            calc_rr == p['rr'] # use constant radius ratio mode
        
        # Only for debugging
        #print("Calc rr: "+str(calc_rr))
        if (calc_rr > 1):
            print("Error in input definition rr > 1")
            break

        out_str += fct_roundrect_gapped_p(p['x_c'], p['y_c'], w, h, calc_rr, p['seg'], p['width'], p['gap'], i<(p['n']-1), gap_con_dir, p['spacing'], layer, False)
    
    if True == header_on:
        out_str += ")"
    return out_str

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
            calc_rr == p['rr'] # use constant radius ratio mode
        
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

# **********************************************************************************
# Coil generation function
# **********************************************************************************

def fct_create_2L_rounded_rect_coil(w_in, h_in, n, gap, const_spacing, spacing, const_r, rr, seg, width):
    out_str = header
    out_str += fct_round_gapped_rect_coil(w_in, h_in, n, gap, 1, const_spacing, spacing, const_r, rr, seg, width, "F.Cu", False)
    out_str += fct_round_gapped_rect_coil(w_in, h_in, n, gap, -1, const_spacing, spacing, const_r, rr, seg, width, "B.Cu", False)
    out_str += ")"
    return out_str

def fct_create_2L_rounded_rect_coil_p(p, header_on):
    out_str = ""
    if True == header_on:
        out_str = header

    out_str += fct_round_gapped_rect_coil_p(p, 1, "F.Cu", False)
    out_str += fct_round_gapped_rect_coil_p(p, -1, "B.Cu", False)

    if True == header_on:
        out_str += ")"
    return out_str

def fct_create_2L_rounded_rect_coil_p_len_res(p, header_on):
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0
    
    if True == header_on:
        out_str = header

    temp_str, temp_len, temp_resistance = fct_round_gapped_rect_coil_p_len_res(p, 1, "F.Cu", False)
    out_str += temp_str
    vect_len += temp_len
    resistance += temp_resistance
        
    temp_str, temp_len, temp_resistance = fct_round_gapped_rect_coil_p_len_res(p, -1, "B.Cu", False)
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
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+p['h_in']/2
        xe = p['x_c']-p['conn_pad_x_spacing']/2
        ye = p['y_c']-p['conn_pad_y_spacing']+p['h_in']/2
        
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "B.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create pad 1
        p['conn_via_ext_con_1']["x"] = xe
        p['conn_via_ext_con_1']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_1'])
        
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+p['h_in']/2
        xe = p['x_c']+p['conn_pad_x_spacing']/2
        ye = p['y_c']-p['conn_pad_y_spacing']+p['h_in']/2

        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "F.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create pad 2
        p['conn_via_ext_con_2']["x"] = xe
        p['conn_via_ext_con_2']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_2'])
        
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        xe = p['x_c']
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "B.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        xe = p['x_c']
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2+p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "F.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create via for layer connection
        p['conn_via_lay']["x"] = xe
        p['conn_via_lay']["y"] = ye
        out_str += fct_via_p(p['conn_via_lay'])
        
    elif p['conn'] == "out": # external connection outside of the coil body
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        xe = p['x_c']-p['conn_pad_x_spacing']/2
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['conn_pad_y_spacing']+p['h_in']/2
        
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "F.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create pad 1
        p['conn_via_ext_con_1']["x"] = xe
        p['conn_via_ext_con_1']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_1'])
        
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+(p['n']-1)*p['spacing']+p['h_in']/2
        xe = p['x_c']+p['conn_pad_x_spacing']/2
        ye = p['y_c']+(p['n']-1)*p['spacing']+p['conn_pad_y_spacing']+p['h_in']/2

        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "B.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create pad 2
        p['conn_via_ext_con_2']["x"] = xe
        p['conn_via_ext_con_2']["y"] = ye
        out_str += fct_via_p(p['conn_via_ext_con_2'])
        
        xs = p['x_c']-p['gap']/2
        ys = p['y_c']+p['h_in']/2
        xe = p['x_c']
        ye = p['y_c']+p['h_in']/2-p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "B.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        xs = p['x_c']+p['gap']/2
        ys = p['y_c']+p['h_in']/2
        xe = p['x_c']
        ye = p['y_c']+p['h_in']/2-p['conn_via_y_spacing']
        
        temp_str, temp_len, temp_resistance = fct_fp_line_len_res(xs, ys, xe, ye, p['width'], "F.Cu")
        out_str += temp_str
        vect_len += temp_len
        resistance += temp_resistance
        
        # Create via for layer connection
        p['conn_via_lay']["x"] = xe
        p['conn_via_lay']["y"] = ye
        out_str += fct_via_p(p['conn_via_lay'])
    else:
        print("No definition for external connection.") # do nothing

    if True == header_on:
        out_str += ")"
    return out_str, vect_len, resistance

def fct_create_2L_rounded_rect_coil_matrix(p, m, n, m_step_over, n_step_over, header_on):
    out_str = ""
    temp_str = ""
    vect_len = 0
    temp_len = 0
    resistance = 0
    temp_resistance = 0
    
    if True == header_on:
        out_str = header
        
    p_ = copy.deepcopy(p)
    for i in range(0, m):
        for j in range(0, n):
            p_['conn_via_ext_con_1']['id_number'] = str(i+1)+str(j+1)+str(0)
            p_['conn_via_ext_con_2']['id_number'] = str(i+1)+str(j+1)+str(1)
            p_['x_c'] = i*m_step_over
            p_['y_c'] = j*n_step_over
            # Only for debugging
            # print(str(p_['x_c'])+" | "+str(p_['y_c']))
            temp_str, temp_len, temp_resistance = fct_create_2L_rounded_rect_coil_p_len_res_conn(p_, False)
            out_str += temp_str
            vect_len += temp_len
            resistance += temp_resistance
            
    if True == header_on:
        out_str += ")"
        
    return out_str, vect_len, resistance

# **********************************************************************************
# Main function
# **********************************************************************************

if __name__ == "__main__":
    
    out, len_, res = fct_create_2L_rounded_rect_coil_matrix(param_2L_coil, 4, 4, 24.4, 20, True)
    #out, len_, res = fct_create_2L_rounded_rect_coil_p_len_res_conn(param_2L_coil, True)
    
    print("Length of total coil winding [mm]: "+str(len_))
    print("Estimated resistance of coil winding [Ohm]: "+str(res))
    try:
        with open(fp_name+file_ending, "x", encoding="utf-8") as f:
            print("File created.")
            f.writelines(out)
    except FileExistsError:
        print('File "'+fp_name+file_ending+'" already exists!')
