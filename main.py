"""
Walks though directories recursively and builds a folder structure based on artist for mp3 files.
"""
import errno

_author = 'ahc'

import eyed3
import os, sys


ILLEGALCHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']


class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush() # If you want the output to be visible immediately
    def flush(self) :
        for f in self.files:
            f.flush()


def main():
   # tee output to file and console
   f = open('log.txt', 'w')
   sys.stdout = Tee(sys.stdout, f)

   cwd = os.getcwd()
   chars = {ord(c):None for c in ILLEGALCHARS}
   dupeid3Dict = {}
   dupefilenameDict = {}
   try:
      os.makedirs(os.path.join(cwd, 'Dupes'))
   except:
      pass # folder exists

   for root, dirs, files in os.walk(cwd, topdown=False):
      for file in files:
         try:
            audiofile = eyed3.load(os.path.join(root,file))
         except ValueError:
            print 'encoding unknown for file:\t%s' % os.path.join(root, file)
         except IOError:
            print 'unable to access file:\t%s' % os.path.join(root, file)

         if not audiofile:
            print '%s is not an mp3 file\n' % file
            continue
         try:
            artist = audiofile.tag.artist
            title = audiofile.tag.title
         except:
            print 'error processing:\t%s' % os.path.join(root, file)
            continue

         # remove illegal characters
         newfile = ''.join([i if ord(i) < 128 else ' ' for i in file])
         if not artist:
            artist = u'Unknown'
         if not title:
            title = u'%s' % newfile

         # remove unicode
         newartist = artist.translate(chars)
         newartist = ''.join([i if ord(i) < 128 else ' ' for i in newartist])

         newtitle = title.translate(chars)
         newtitle = ''.join([i if ord(i) < 128 else ' ' for i in newtitle])

         newdir = os.path.join(cwd,newartist)
         if not os.path.exists(newdir):
            os.makedirs(newdir)

         if dupeid3Dict.get('%s|%s' % (newartist, newtitle)) or dupefilenameDict.get(newfile) or (os.path.exists(os.path.join(newdir, newfile)) and not os.path.join(newdir, newfile) == os.path.join(root, newfile)):
            try:
               os.rename(os.path.join(root, file), os.path.join(os.path.join(cwd, 'Dupes'), newfile))
               # delete dir if empty
               try:
                  os.rmdir(root)
               except OSError as e:
                  if e.errno == errno.ENOTEMPTY:
                     pass # directory not empty, don't delete
               continue
            except:
               print 'couldn\'t move file to dupes: \t%s, keeping old location...' % os.path.join(root, file)
               continue

         try:
            os.rename(os.path.join(root, file), os.path.join(newdir, newfile))
         except:
            print 'couldn\'t move file: \t%s, keeping old location...' % os.path.join(root, file)
            continue

         # delete dir if empty
         try:
            os.rmdir(root)
         except OSError as e:
            if e.errno == errno.ENOTEMPTY:
               pass # directory not empty, don't delete

         dupeid3Dict['%s|%s' % (newartist, newtitle)] = None
         dupefilenameDict[newfile] = None


if __name__ == '__main__':
    main()