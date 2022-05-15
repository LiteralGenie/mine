from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

### config

im_dir = '/home/anne/Pictures/test/'

prefix = 't2_'
prefix_out = 'out_'
ext = 'png'

normalize_dims = True # whether to pad images so they have the same size

border_width = 20
border_color = (50,)*3

orientation = 'h' # (h)oriztonal or (v)ertical stitching

captions = [
    "test",
    "test234",
    "whatever"
]
text_color = (255,)*3
text_size = 75
line_height = 125
font_path = './fonts/RobotoMono-Bold.ttf'
text_background_color = (125,)*3

background_color = (0,0,0) # only visible when images have different sizes

### not config

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

hdlr = logging.StreamHandler()
hdlr.setLevel(logging.DEBUG)

fmtr = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

hdlr.setFormatter(fmtr)
log.addHandler(hdlr)

### really not config

if __name__ == '__main__':
    Point2d: tuple[int, int]
    Point3d: tuple[int, int, int]
    Point4d: tuple[int, int, int, int]

    def _pad(im: Image, dims: Point4d, color: Point3d = (0,0,0)) -> Image:
        """Pad image edges

        Parameters
        ----------
        im: -
        dims: (top, right, bottom, left)
        color: -
        """
        
        dest_dims = (
            im.size[0] + dims[1] + dims[3],
            im.size[1] + dims[0] + dims[2]
        )
        dest = Image.new(im.mode, dest_dims, color)
        dest.paste(im, (dims[1], dims[0]))
        return dest

    def _write_top(
        text: str,
        im: Image,
        text_color: Point3d = (255, 255, 255),
        background_color: Point3d = (0, 0, 0)
    ):
        """Write text above image
        """

        dest = _pad(im.copy(), (line_height, 0,0,0), background_color)

        ctx = ImageDraw.Draw(dest)
        font = ImageFont.truetype(font_path, text_size)
        anchor_point = (im.size[0] // 2, line_height // 2)

        ctx.text(anchor_point, text, anchor='mm', font=font, fill=text_color)

        return dest

    def _concat_vert(images: list[Image], overlap=0):
        widths = [im.size[0] for im in images]
        heights = [im.size[1] for im in images]
        dims = (max(widths), sum(heights))

        canvas = Image.new(images[0].mode, dims, background_color)
        current_y = 0
        for im in images:
            pos = (0, current_y)
            canvas.paste(im, pos)
            current_y += im.size[1] - overlap
        
        return canvas

    def _concat_horiz(images: list[Image], overlap=0):
        widths = [im.size[0] for im in images]
        heights = [im.size[1] for im in images]
        dims = (sum(widths), max(heights))

        canvas = Image.new(images[0].mode, dims, background_color)
        current_x = 0
        for im in images:
            pos = (current_x, 0)
            canvas.paste(im, pos)
            current_x += im.size[0] - overlap
        
        return canvas

    def _normalize_dims(images: list[Image]):
        dests = [im.copy() for im in images]

        widths = [im.size[0] for im in dests]
        heights = [im.size[1] for im in dests]
        padded_size = (max(widths), max(heights))

        for (idx, im) in enumerate(dests):
            diff_width = padded_size[0] - im.size[0]
            diff_height = padded_size[1] - im.size[1]

            if diff_width != 0 or diff_height != 0:
                padding = (0, diff_width, diff_height, 0)
                dests[idx] = _pad(im, padding, background_color)

        for idx, (im, dst) in enumerate(zip(images, dests)):
            dests[idx] = _checker(dst)
            dests[idx].paste(im, (0,0))
            
        return dests

    def _checker(image: Image, light=(150,)*3, dark=(100,)*3, square_size=15):
        assert (image.size[0] > square_size) and (image.size[1] > square_size), f'Can\'t checker a {image.size} image with {square_size}x{square_size} squares. Too small!'

        dest = Image.new(image.mode, image.size)

        white_square = Image.new(image.mode, (square_size, square_size), light)
        black_square = Image.new(image.mode, (square_size, square_size), dark)

        row_white = Image.new(image.mode, (image.size[0], square_size))
        row_black = Image.new(image.mode, (image.size[0], square_size))

        ind_x = 0
        ind_square = 0
        squares = (white_square, black_square)
        while ind_x < image.size[0]:
            ind_white = ind_square
            ind_black = (ind_square + 1) % 2

            row_white.paste(squares[ind_white], (ind_x, 0))
            row_black.paste(squares[ind_black], (ind_x, 0))

            ind_x += square_size
            ind_square = (ind_square + 1) % 2
        
        ind_y = 0
        ind_row = 0
        rows = [row_white, row_black]
        while ind_y < image.size[1]:
            dest.paste(rows[ind_row], (0, ind_y))

            ind_y += square_size
            ind_row = (ind_row + 1) % 2

        return dest

    def stitch() -> Image:
        # load images
        paths = Path(im_dir).glob(f'{prefix}*.{ext}')
        paths = list(sorted(paths, key=lambda fp: fp.name))
        images = [Image.open(fp) for fp in paths]
        log.info(f'targets: {[x.name for x in paths]}')
        log.debug(f'image dims: {[x.size for x in images]}')

        if normalize_dims:
            images = _normalize_dims(images)

        # add text
        dests = [im for im in images]
        for idx in range(len(images)):
            text = captions[idx] if (idx < len(captions)) else ""
            dests[idx] = _write_top(text, dests[idx], text_color, text_background_color)
        
        # draw borders
        dests = [_pad(im, (border_width,)*4, border_color) for im in dests]

        # stitch
        concat_op = _concat_horiz if orientation == 'h' else _concat_vert
        stitched = concat_op(dests, border_width)

        # done
        return stitched

    out_path = Path(im_dir) / f'{prefix_out}{prefix}.{ext}'

    out_image = stitch()
    out_image.save(out_path)

    log.info(f'created {out_path}')