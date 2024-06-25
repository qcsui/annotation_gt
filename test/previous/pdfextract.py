import io
import os
import pdfplumber
import plotly.express as px
import plotly.graph_objects as go
from operator import itemgetter
from PIL import Image, ImageDraw, ImageFont
import fitz
import time
import torch
# import cv2
import numpy as np
from PIL import Image
from centernet_powerbrain import CenterNet
from cutting import cutting
import os


def extract_one_curve(curve, coH, coV, Ox, Oy, fig_x, fig_y):
    points_list0 = curve["pts"]
    # points_list0x = points_list0[0][0]
    # points_list0y = points_list0[0][1]
    list0 = map(lambda p: ((p[0] - fig_x) * coH + Ox, (p[1] - fig_y) * coV + Oy), points_list0)
    # print(list(list0))
    result0 = list(list0)
    return result0


def extr_titles_text(page, x0, bottom, x1, top):
    title_up = page.within_bbox((x0 - 15, top - 25, x1, top),
                                relative=False, strict=True).extract_text(keep_blank_chars=True, x_tolerance=10)
    # title left
    title_left = page.within_bbox((x0 - 35, top - 25, x0 - 10, bottom + 20),
                                  relative=False, strict=True).extract_text(keep_blank_chars=True,
                                                                            x_tolerance=10,
                                                                            use_text_flow=True)
    # title bottom
    title_bn = page.within_bbox((x0 - 10, bottom + 10, x1 + 10, bottom + 30),
                                relative=False, strict=True).extract_text(keep_blank_chars=True, x_tolerance=10)
    return title_up, title_left, title_bn


def extr_titles(page, x0, bottom, x1, top):
    title_up = page.within_bbox((x0 - 15, top - 25, x1, top),
                                relative=False, strict=True).extract_words(keep_blank_chars=True,
                                                                           x_tolerance=10,
                                                                           use_text_flow=True)
    # title left
    title_left = page.within_bbox((x0 - 35, top - 25, x0 - 10, bottom + 20),
                                  relative=False, strict=True).extract_words(keep_blank_chars=True,
                                                                             x_tolerance=10,
                                                                             use_text_flow=True)
    # title bottom
    title_bn = page.within_bbox((x0 - 10, bottom + 10, x1 + 10, bottom + 30),
                                relative=False, strict=True).extract_words(keep_blank_chars=True,
                                                                           x_tolerance=10,
                                                                           use_text_flow=True)
    return title_up, title_left, title_bn


def extr_legend(page, x0, bottom, x1, top):
    legend = page.within_bbox((x0 + 5, top + 5, x1 - 5, bottom - 5),
                              relative=False, strict=True).rects
    legend_lines = [page.within_bbox((legend[0]["x0"], legend[0]["top"],
                                      legend[0]["x1"], legend[0]["bottom"]),
                                     relative=False, strict=True).lines]
    # legend_text=pdf.pages[1].within_bbox((legend_lines[0]["x1"], legend_lines[0]["top"]-5,
    #                                              legend_lines[0]["x1"]+40, legend_lines[0]["bottom"]+5),
    #                                      relative=False, strict=True).extract_words()
    legend_text = [page.within_bbox((ll["x1"], ll["top"] - 5, ll["x1"] + 40, ll["bottom"] + 7), relative=False,
                                    strict=True).extract_words(keep_blank_chars=True, x_tolerance=10, y_tolerance=1,
                                                               use_text_flow=True) for ll in legend_lines]

    return legend_lines, legend_text


def extr_coor(page, fig, fig_list0_x0, fig_list0_bottom, fig_list0_x1, fig_list0_top):
    axis_list_Vdown = page.within_bbox((fig_list0_x0 - 15, fig_list0_bottom - 15,
                                        fig_list0_x0, fig_list0_bottom + 14),
                                       relative=False, strict=True).extract_words(x_tolerance=0.5, y_tolerance=0.1)
    axis_list_Vup = page.within_bbox((fig_list0_x0 - 15, fig_list0_top - 5,
                                      fig_list0_x0, fig_list0_top + 35),
                                     relative=False, strict=True).extract_words(x_tolerance=0.5, y_tolerance=0.1)
    axis_list_Hright = page.within_bbox((fig_list0_x1 - 15, fig_list0_bottom - 5,
                                         fig_list0_x1 + 15, fig_list0_bottom + 20),
                                        relative=False, strict=True).extract_words(x_tolerance=0.5, y_tolerance=0.1)
    axis_list_Hleft = page.within_bbox((fig_list0_x0 - 10, fig_list0_bottom + 1,
                                        fig_list0_x0 + 15, fig_list0_bottom + 20),
                                       relative=False, strict=True).extract_words(x_tolerance=0.5, y_tolerance=0.1)

    # debug
    # im = page.to_image(resolution=150)
    # im.draw_rects([{"x0":fig_list0_x0-15,
    #                "top":fig_list0_bottom-5,
    #                "x1":fig_list0_x0,
    #                "bottom":fig_list0_bottom+4 }])
    #
    # first horiz line
    horizontal_edges0 = page.within_bbox((fig_list0_x0 - 5, fig_list0_top + 3,
                                          fig_list0_x1 + 5, fig_list0_top + 65),
                                         relative=False, strict=True).horizontal_edges

    # im = page.to_image(resolution=150)
    # im.draw_rects(horizontal_edges0)
    # print("horizontal_edges0",horizontal_edges0[0])

    # im.show()
    # selected_edge0= [x  for x in horizontal_edges0 if x["width"] > 60 and x["stroking_color"][0]>0.1]
    selected_edge0 = [x for x in horizontal_edges0 if x["width"] > 60]

    # find height of axes
    topline = max(selected_edge0, key=itemgetter("y0"))
    # topline= [max(x,key=itemgetter("y0"))  for x in horizontal_edges0 if x["width"] > 50 and x["stroking_color"][0]>0.2]
    # print(topline)
    height_axes = topline['y1'] - fig['y0']
    height_axes = height_axes if height_axes > fig['height'] * 0.88 else fig['height']
    # print("height_axes=  ",height_axes)
    # print("axis_list_Vdown", axis_list_Vdown)
    # print("axis_list_Vup",axis_list_Vup)
    # print("axis_list_Hright",axis_list_Hright)
    # print("axis_list_Hleft",axis_list_Hleft)

    # prepare for curves
    Hright = float(axis_list_Hright[0]['text'])
    Hleft = float(axis_list_Hleft[0]['text'])
    Vup = float(axis_list_Vup[0]['text'])
    Vdown = float(axis_list_Vdown[0]['text'])
    width0 = fig['width']
    # print("width0=  ",width0,"Hleft=",Hleft,"Hright=",Hright,Vup,Vdown)
    coH = (Hright - Hleft) / width0
    coV = (Vup - Vdown) / height_axes
    return coH, coV, Hleft, Vdown


def sort_boxes(boxes):
    return sorted(
        boxes,
        key=lambda box: (box["top"] * 30 + box["x0"]),
        # reverse=True
    )


## main
def pdf_main(filedir, pageno, figno):
    pageno = pageno - 1
    figno = figno - 1
    with pdfplumber.open(filedir) as pdf:
        # curves_list = current_page.curves
        current_page = pdf.pages[pageno]
        rects_list = current_page.rects

        # filter and select figure
        RECTS_WIDTH_LOWER = 120
        RECTS_WIDTH_UPPER = 400
        RECTS_HEIGHT_LOWER = 120
        RECTS_HEIGHT_UPPER = 230
        fig_list = [
            x for x in rects_list
            if RECTS_WIDTH_LOWER < x["width"] < RECTS_WIDTH_UPPER
               and RECTS_HEIGHT_LOWER < x["height"] < RECTS_HEIGHT_UPPER
        ]

        # fig_list= [x  for x in rects_list if x["width"]>120 and x["width"]<400 and x["height"]>120 and x["height"]<400]
        fig_list = sort_boxes(fig_list)  # sort by top and x0

        # im = current_page.to_image(resolution=150)
        current_fig = fig_list[figno]
        # print(curves_list[0])

        # Axes
        fig_list0_x0 = current_fig['x0']
        fig_list0_bottom = current_fig['bottom']
        fig_list0_x1 = current_fig['x1']
        fig_list0_top = current_fig['top']

        fig_list0_y0 = current_fig['y0']
        fig_list0_top = current_fig['top']
        fig_list0_height = current_fig['height']
        try:

            coH, coV, Ox, Oy = extr_coor(current_page, current_fig, fig_list0_x0, fig_list0_bottom, fig_list0_x1,
                                         fig_list0_top)
        except:
            print("error in extr_coor")
            return
        curve_list = current_page.within_bbox(
            (fig_list0_x0 - 15, fig_list0_top - 15, fig_list0_x1 + 15, fig_list0_bottom + 15),
            relative=False, strict=True).curves
        curves_results = [extract_one_curve(x, coH, coV, Ox, Oy, fig_list0_x0, fig_list0_y0) for x in curve_list]
        curves_color = [x["stroking_color"] for x in curve_list]

        title_txt = extr_titles(current_page, fig_list0_x0, fig_list0_bottom, fig_list0_x1, fig_list0_top)

        fig = go.Figure()
        # ccc=curves_results[0]
        for idx, i in enumerate(curves_results):
            fig.add_trace(go.Scatter(x=[d[0] for d in i], y=[d[1] for d in i],
                                     mode='lines',
                                     name=idx))
        fig.update_layout(

            width=700, height=580,
            title=title_txt[0][0]["text"],
            xaxis_title=title_txt[2][0]["text"],
            yaxis_title=title_txt[1][0]["text"],
            legend_title="Legend",
            #     title={
            #         'text': ttt[0][0]["text"],
            #         'font': {
            #     'size': 14  # set the font size to 24
            # }},
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="black"
            ),
            # legend=dict(
            #     yanchor="top",
            #     y=0.01,
            #     xanchor="left",
            #     x=0.05
            # ),
        )
        return fig.to_html(), fig.to_json()


def preview(filedir, pageno=2):
    pageno = pageno - 1

    with pdfplumber.open(filedir) as pdf:
        # curves_list = current_page.curves
        current_page = pdf.pages[pageno]
        rects_list = current_page.rects

        # select figure
        RECTS_WIDTH_LOWER = 120
        RECTS_WIDTH_UPPER = 400
        RECTS_HEIGHT_LOWER = 120
        RECTS_HEIGHT_UPPER = 230
        fig_list = [
            x for x in rects_list
            if RECTS_WIDTH_LOWER < x["width"] < RECTS_WIDTH_UPPER
               and RECTS_HEIGHT_LOWER < x["height"] < RECTS_HEIGHT_UPPER
        ]
        fig_list = sort_boxes(fig_list)
        # fig_list.sort(key=lambda box: (box["top"] * 30 + box["x0"]))
        im = current_page.to_image(resolution=25)
        # im = current_page.to_image(resolution=150)
        # current_fig=fig_list[figno]
        img_byte_arr = io.BytesIO()
        im.save(img_byte_arr, format='JPEG')
        # print(img_byte_arr.fileno) #debug
        image_buffer = io.BytesIO(img_byte_arr.getvalue())
        print("load image_buffer")
        image = Image.open(image_buffer)
        draw = ImageDraw.Draw(image)
        font_path = "./CONSOLA.TTF"  # debug
        font_size = 50
        font = ImageFont.truetype(font_path, font_size)
        # font = ImageFont.load_default()  CONSOLA.TTF
        # print("load ./CONSOLA.TTF")
        for idx, fig in enumerate(fig_list):
            print(idx)
            letter = str(idx + 1)
            position = (10 + fig['x0'] / 3, 10 + fig['top'] / 3)
            print("x0:", fig['x0'])
            print("top:", fig['top'])
            print("position:", position)
            draw.text(position, letter, font=font, fill=(255, 0, 0, 50))  # Black
        # image.show() #debug
        img_byte_return = io.BytesIO()
        image.save(img_byte_return, 'JPEG')
        img_byte_return.seek(0)
        return img_byte_return


# function to preview all pages of pdf
def preview_allpages(filedir):
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, 'static', 'CONSOLA.TTF')
    print(font_path)
    desired_dpi = 25
    font_size = 40
    fint_size_pageno = 20
    # Calculate zoom factor based on desired DPI resolution
    zoom = desired_dpi / 72  # Default DPI in PDF is 72
    ratio = 72 / desired_dpi
    try:
        doc = fitz.open(filedir)
    except Exception as e:
        print(f"An error occurred: {e}")
    print('pdf2iamgesdone')

    # static_dir = os.path.join(app.root_path, 'static')
    # filedir = os.path.join(static_dir, 'CONSOLA.TTF')
    # font_path = "./static/CONSOLA.TTF"
    re_list = []
    with pdfplumber.open(filedir) as pdf:

        for p_idx, current_page in enumerate(pdf.pages):
            try:
                # print(f"Page {p_idx+1}: {current_page.width} x {current_page.height}")
                rects_list = current_page.rects
                # filter and select figure
                RECTS_WIDTH_LOWER = 120
                RECTS_WIDTH_UPPER = 400
                RECTS_HEIGHT_LOWER = 120
                RECTS_HEIGHT_UPPER = 230
                fig_list = [
                    x for x in rects_list
                    if RECTS_WIDTH_LOWER < x["width"] < RECTS_WIDTH_UPPER
                       and RECTS_HEIGHT_LOWER < x["height"] < RECTS_HEIGHT_UPPER
                ]

                # fig_list= [x  for x in rects_list if x["width"]>120 and x["width"]<400 and x["height"]>120 and x["height"]<230]
                # if not fig_list:
                #     continue
                fig_list = sort_boxes(fig_list)  # sort by top and x0
                # print("sort_boxes"+fig_list)        #debug
                # fig_list.sort(key=lambda box: (box["top"] * 10 + box["x0"])) #sort by top and x0
                # im = current_page.to_image(resolution=25)
                # Perform further operations with the image
                # print("current_page.to_image")        #debug
                # im.draw_rects(fig_list)
                # print("im.draw_rects(fig_list)")        #debug
                # img_byte_arr = io.BytesIO()
                # im.save(img_byte_arr, format='JPEG')
                mupage = doc.load_page(p_idx)
                mat = fitz.Matrix(zoom, zoom)
                pix = mupage.get_pixmap(matrix=mat, alpha=False)
                # pix = page.get_pixmap(alpha=False, matrix=mat)
                # Get the image dimensions and mode
                width, height = pix.width, pix.height
                mode = "RGBA" if pix.alpha else "RGB"
                # Create a Pillow Image object using the image data from the Pixmap object
                image = Image.frombytes(mode, (width, height), pix.samples)
                # img_byte_arr = io.BytesIO(pix.tobytes("jpeg", "RGB"))
                # print(img_byte_arr.fileno) #debug
                # image_buffer = io.BytesIO(img_byte_arr.getvalue())
                # print("load image_buffer")
                # image = Image.open(image_buffer)
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype(font_path, font_size)
                font_page = ImageFont.truetype(font_path, fint_size_pageno)
                # font = ImageFont.load_default()  CONSOLA.TTF
                # print("load CONSOLA.TTF")
                draw.text((10, 10), 'Page' + str(p_idx + 1), font=font_page, fill=(255, 90, 30))  # Black

                for idx, fig in enumerate(fig_list):
                    letter = str(idx + 1)

                    position = (fig['x0'] / ratio, fig['top'] / ratio)  # 2.88=72/25
                    # print('index:',letter)
                    # print("x0:", fig['x0'])
                    # print("top:", fig['top'])
                    # print("position:", position)
                    rectangle_coords = [position,
                                        (position[0] + (fig["width"] / 2.88), position[1] + (fig["height"] / 2.88))
                                        # Adjust the size of the rectangle based on the font size
                                        ]
                    # Draw the rectangle
                    draw.rectangle(rectangle_coords, fill=None, outline=(255, 90, 30))
                    draw.text((position[0] + 10, position[1] + 10), letter, font=font, fill=(255, 90, 30))  # Black
                # image.show() #debug
                img_byte_return = io.BytesIO()
                img_byte_return.seek(0)
                image.save(img_byte_return, 'GIF', optimize=True)
                # image.save(img_byte_return, 'JPEG',quality=80)
                # image.save(img_byte_return, 'PNG',optimize = True)
                img_byte_return.seek(0)
                re_list.append(img_byte_return)
            except Exception as e:
                print(f"An error occurred: {e}")
        return re_list


def preview_allpages_CNN(filedir):
    centernet = CenterNet()
    re_list = []
    #    pdf_name = []
    #    pdf_dir = 'pdf/pdf'  # Put orginal datasheet into this folder
    #    pdf_name = os.listdir(pdf_dir)[0]
    #
    # combine pdf_dir with pdf_name as a path
    #    pdf_path = os.path.join(pdf_dir, pdf_name)

    cutting.seperatepdf(filedir)

    with fitz.open(filedir) as pdfDoc:
        # for i in range(pdfDoc.pageCount):  #语法更新
        for page in pdfDoc:
            zoom_x = 25 / 72  # horizontal zoom
            zoom_y = 25 / 72  # vertical zoom
            mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
            pix = page.get_pixmap(matrix=mat)  # use 'mat' instead of the identity matrix
            # pix.save("page.png" % page.number)
            # Store the image in a data buffer
            image_buffer = pix.tobytes("png")
            # Create a Pillow Image from the data buffer
            image = Image.open(io.BytesIO(image_buffer))
            #
            # pages_dir = 'pdf/pages'
            # pages_name = os.listdir(pages_dir)
            # boxes = []
            # for i in range(len(pages_name)):
            #     #k = 0
            #     pages_path = os.path.join(pages_dir, pages_name[i])
            image, boxes = centernet.detect_image(image, page.number)
            # if isinstance(boxes,int):
            #    boxes = 0
            # else:
            #   for j in range(len(boxes)):
            #      cutting.cutfigures(pages_path,pages_name[i],boxes[j],k)
            #     k += 1

            print(boxes)
            image.show()
            img_byte_return = io.BytesIO()
            img_byte_return.seek(0)
            image.save(img_byte_return, 'GIF', optimize=True)
            # image.save(img_byte_return, 'JPEG',quality=80)
            # image.save(img_byte_return, 'PNG',optimize = True)
            img_byte_return.seek(0)
            re_list.append(img_byte_return)

    return re_list