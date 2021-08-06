#!/usr/bin/sh

rm -rf target
mkdir -p target

cd addons/
zip ../target/ExplainerUtils.zip -r explainer_utils/*.py explainer_utils/*/*.py
cd ..

mkdir -p target/Explainer/
cp Template.blend target/Explainer/startup.blend
cd target/
zip ./ExplainerTemplate.zip -r Explainer/
rm -rf Explainer/
cd ../

cp Midnight.xml ./target/
