# Site — Vidraçaria do Adilson

Site estático (HTML, CSS e JS) de www.vidracariadoadilson.com.br.

- `site/` — o site pronto, publicado pela hospedagem (pasta de saída).
- `fonte/` — o gerador e os conteúdos (serviços, bairros, blog, serviços realizados, fotos, logo).

## Como atualizar
1. Edite os conteúdos em `fonte/` (ex.: `services_a.py`, `local_posts.py`, `projects.py`).
2. Gere o site: `python3 fonte/build.py site`
3. Confira: `python3 fonte/check.py site`
4. Faça commit e push — a hospedagem publica sozinha.

## Hospedagem
- Cloudflare Pages: comando de build vazio, pasta de saída `site`.
- Vercel: usa o `vercel.json` (pasta de saída `site`).
