package com.atlas;

import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;

import javax.imageio.ImageIO;

/** Vision models bill a picture by its size, in tiles of 512 by 512 pixels. A photo that fits in one tile costs about
 *  a third of an 800 by 600 one, and the model still sees an exhibit perfectly well. */
public final class Photos {

    private Photos() {
    }

    /** The photo as a JPEG whose longer side is at most maxSide pixels (smaller photos are left at their size). */
    public static byte[] shrink(byte[] photo, int maxSide) throws IOException {
        BufferedImage in = ImageIO.read(new ByteArrayInputStream(photo));
        if (in == null) {
            throw new IOException("That file is not a picture Atlas can read (send a JPEG or PNG).");
        }
        double scale = Math.min(1.0, (double) maxSide / Math.max(in.getWidth(), in.getHeight()));
        int w = Math.max(1, (int) Math.round(in.getWidth() * scale));
        int h = Math.max(1, (int) Math.round(in.getHeight() * scale));
        BufferedImage out = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = out.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g.drawImage(in, 0, 0, w, h, null);
        g.dispose();
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        ImageIO.write(out, "jpg", bytes);
        return bytes.toByteArray();
    }
}
