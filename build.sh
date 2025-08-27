pyinstaller --onefile rtp.py
pyinstaller --onefile --noconsole rtp-gui.py
cp -f readme.txt dist/
cp -f LICENSE dist/
cp -rf texts/ dist/
rm rtp.spec rtp-gui.spec
cd dist
7z a rtp.zip *
mv rtp.zip ../
cd ..
