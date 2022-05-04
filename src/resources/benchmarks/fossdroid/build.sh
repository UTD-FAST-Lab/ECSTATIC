#!/bin/bash

CUR=$(pwd)
cd /
git clone https://github.com/Pancax/AlarmKlock_Android.git
cd AlarmKlock_Android

if [ ! -f ./build.sh ]; then
      echo "#!/bin/bash" > ./build.sh
      echo "./gradlew assemble" >> ./build.sh
      chmod +x build.sh
fi

./build.sh
cd $CUR