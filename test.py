def square_subsequent_mask(size):
    mask = (torch.triu(torch.ones((size, size), device=device)) == 1).transpose(0, 1)
    mask = (
        mask.float()
        .masked_fill(mask == 0, float("-inf"))
        .masked_fill(mask == 1, float(0.0))
    )
    return mask


def model_predict(
    model, src, src_mask, max_len, sos_idx=SOS_IDX, eos_idx=EOS_IDX, device=device
):
    src = src.to(device)
    src_mask = src_mask.to(device)

    embedding = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(sos_idx).long().to(device)
    for i in range(max_len - 1):
        embedding = embedding.to(device)
        if i == 0:
            ys = ys.transpose(1, 0)
        tgt_mask = (square_subsequent_mask(ys.size(1)).type(torch.bool)).to(device)
        out = model.decode(ys, embedding, tgt_mask)
        prob = model.out_layer(out[:, -1])
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.item()
        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
        if next_word == eos_idx:
            break
    return ys


def translate_sentence(
    model: torch.nn.Module, src_sentence: Tensor, trg_vocab=vocab_en
):
    model.eval()
    src = src_sentence.view(1, -1)
    num_tokens = src.shape[1]
    src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
    tgt_tokens = model_predict(model, src, src_mask, max_len=num_tokens + 5).flatten()
    return (
        " ".join(vocab_en.lookup_tokens(list(tgt_tokens.cpu().numpy())))
        .replace("<sos> ", "")
        .replace(" <eos>", "")
    )
