from kai.tokenizer.tokenizer import Tokenizer


tk = Tokenizer()


# finish sb into the builder
def finish(builder, sb):
    if len(sb) > 0:
        if len(builder) == 0:
            builder.append(' '.join(sb))
            sb = []
        else:
            new_builder = []
            for str1 in builder:
                str3 = [str1, " "] + sb
                new_builder.append(' '.join(str3))
            return new_builder, []
    elif len(builder) == 0:
        builder.append("")
    return (builder, [])


# expand around brackets and stuff
def expand_brackets(pattern: str):
    if "(" in pattern:
        token_list = tk.filter_spaces(tk.tokenize_string(pattern))
        builder = []
        sb = []
        i = 0
        while i < len(token_list):
            text = token_list[i]
            if text == "(":
                builder, sb = finish(builder, sb)
                item_list = []
                j = i + 1
                item = []
                while j < len(token_list):
                    t2 = token_list[j]
                    if t2 == ")":
                        item_list.append(' '.join(item))
                        j += 1
                        break
                    elif t2 == "|":
                        item_list.append(' '.join(item))
                        item = []
                    else:
                        if len(item) > 0:
                            item.append(" ")
                        item.append(t2)
                    j += 1

                new_builder = []
                for str1 in builder:
                    for str2 in item_list:
                        str3 = str1 + " " + str2
                        new_builder.append(str3.strip())
                builder = new_builder
                i = j

            else:
                sb.append(text)
                i += 1

        builder, sb = finish(builder, sb)
        return builder

    else:
        return [pattern]
