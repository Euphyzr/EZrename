## EZrename
Bulk renames files and directories with handy options.

## Usage
basic: `EZrename [-h] [-v] [-a] {rename,config} ...`

### For renaming
usage: ```EZrename rename [-h] [-r REGEX | -pr PRESET_REGEX] [-i [IGNORE [IGNORE ...]]] 
          [-o [ONLY [ONLY ...]]] [-d] [-u] [-q]```
Suppose we have a directory with the contents:
```
[example] exampledir1/  [example] exampledir2/  [example] exampledir3/
[example] examplevid 1 (2020-11-13).mp4         [example] examplevid2 (2020-11-13).mp4
[example] examplesound3 (2020-11-05).mp3        [example] text.txt
[example] text2.txt  docu.docx  docu2.docx
```
We want to replace all the [example] to [something] from here:<br/>
`EZrename rename X:\path\to\target\directory [something] -r \[example\]`<br/>
**[Note]** Since the matching works using regular expressions, we have to escape the [] brackets with \.<br/><br/>

On second thought, you want to keep [example] for the a file with certain extension or directories only.
#### The following options will come in handy:
`-o/--only [ONLY [ONLY ...]]` - only apply renaming on certain extensions. Example: `-o mp4 mp3 txt`<br/>
`-i/--ignore [IGNORE [IGNORE ...]]` - ignores renaming on certain extensions.<br/>
`-d/--directory` - Now this has different behaviours. Calling only --directory will rename only directories.
Calling it with --only will rename only directories and those extensions. Calling it with --ignore will ignore directories and those extensions. Calling it only --directory and --ignore with no provided extensions will only
ignore directories.<br/><br/>
**[Example]** To rename only directories and text files: `EZrename rename X:\path\to\target\directory [something] -r \[example\] -d -o txt`<br/><br/>
You can also use -u/--undo to undo the changes. But you can go back only 1 batch of rename.<br/>
`EZrename rename X:\path\to\target\directory -u`

## For configuration
usage: ```EZrename config [-h] [-dp [DEFAULT_PRESET]] [-pl] [-pa NAME PATTERN] [-pd NAME [NAME ...]]```<br/><br/>

If there's a pattern we have to deal with a lot. We can just set it to default so that we don't need to use
`-r` everytime when renaming. Like:<br/>
`EZrename config -d \[example\]`<br/>
So, next time we can just do, `EZrename rename path\to\target [seomthing] ...`.<br/>
Other than default one, other presets can be made. Like: `EZrename config --preset-add example \[example\]`<br/>
#### Other configuration related options:<br/>
`-pl/--preset-list`                  - List all presets<br/>
`pd/--preset-delete NAME [NAME ...]` - Delete one or multiple presets by name<br/>
`-dp/--default-preset [PATTERN]`     - Set a default preset. Not providing any pattern shows the current preset.<br/>