def fix_file_output(file: str) -> None:
    content = ""
    with open(file) as f:
        for l in f:
            content += l

    content = content.replace('soot.jimple.infoflow.android.SetupApplication$InPlaceInfoflow',
                              'soot.jimple.infoflow.Infoflow')

    with open(args.file, 'w') as f:
        f.write(content)
