## EZrename
Bulk renames files and directories with handy options

## Usage
`path/to/target/directory
IMG_1.png  IMG_2.png  IMG_3.mp4  IMG_Collection/`
Suppose we want to rename them to 'Summer Vacation - '
```
"path/to/EZrename.py" --path "path/to/target/directory" --replacewith "Summer Vacation - " --regex IMG_
```
Actually, on second thought lets keep the directory and mp4 file untouched. So, let's undo the changes
```
"path/to/EZrename.py" --undo
```
Now, leaving directory and mp4 files untouched can be done in two ways
```
"path/to/EZrename.py" -p "path/to/target/directory" -w "Summer Vacation - " -r IMG_ --only png
```
or,
```
"path/to/EZrename.py" -p "path/to/target/directory" -w "Summer Vacation - " -r IMG_ --ignore directory mp4
```
If there's a pattern that comes across a lot, that can be set as default regex. Then we can avoid -r/--regex
```
"path/to/EZrename.py" --regex-default "default regex pattern"
```
Regex patterns can also be saved as presets for later uses
```
"path/to/EZrename.py" --regex-add images IMG_
"path/to/EZrename.py" -p "path/to/target/directory" -w "Summer Vacation - " --preset-regex images
```
Presets can be deleted. E.g `-rd/--regex-delete images`

For detailed help, `"path/to/EZrename.py" --help
