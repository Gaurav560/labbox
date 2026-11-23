package com.setu;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Chapter 3: run with  mvn -q compile exec:java */
public class Setu {

    public static void main(String[] args) throws IOException {
        List<String> lines = Files.readAllLines(Path.of("announcements.txt"));
        System.out.println("== A bag of words");
        System.out.println(Words.count(String.join(" ", lines)));

        System.out.println("\n== A bigram model, trained on " + lines.size() + " station announcements");
        Bigram model = new Bigram();
        model.train(lines);
        for (String w : new String[] {"the", "ghat", "running", "platform", "lonavala"}) {
            System.out.println("after '" + w + "' comes '" + model.next(w) + "'");
        }
        System.out.println("\n" + model.generate("the", 12));
    }
}
