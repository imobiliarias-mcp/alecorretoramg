# Reverse-Engineered API Specification: Alê Corretora MG

## 1. Overview & Architecture

Alê Corretora MG (`https://alecorretoramg.com.br`) is a real estate agency portal built on top of **WordPress** with **Elementor Pro**, **Crocoblock JetEngine** (custom post type `imoveis`), and **Crocoblock JetSmartFilters**.

The site renders listing archives via an asynchronous AJAX endpoint (`/wp-admin/admin-ajax.php`) using the `jet_smart_filters` action with dynamic HTML template injection (`jet-listing-grid--6919`). Property details are served as server-side rendered HTML with Elementor widgets, including full-resolution photo carousels.

### 1.1 Authentication & Security Requirements
- **Authentication**: **None required**. All property searches, filter queries, pagination requests, property details, and gallery photos are publicly accessible without authentication, credentials, cookies, or CSRF tokens.
- **Request Headers**:
  - `User-Agent`: Desktop browser User-Agent is required to pass Hostinger CDN / WAF rules.
  - `Accept`: Standard browser Accept headers (e.g. `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` or `application/json, text/javascript, */*; q=0.01`).
  - `X-Requested-With`: `XMLHttpRequest` for AJAX endpoints.
- **HTTP Methods**:
  - Search / Filtering / Pagination: `POST` to `/wp-admin/admin-ajax.php`.
  - Property Detail Retrieval: `GET` to `/?p={post_id}` (HTTP 301 redirect to canonical slug) or direct canonical `GET` to `/imoveis/{slug}/`.
  - Taxonomy & Location Metadata: `GET` to `/wp-json/wp/v2/{taxonomy}`.

---

## 2. Search & Rental Listing Endpoints

The search engine is driven by JetSmartFilters attached to the JetEngine query provider `jet-engine/todos`.

### 2.1 Primary Search Endpoint

```http
POST /wp-admin/admin-ajax.php HTTP/1.1
Host: alecorretoramg.com.br
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Accept: application/json, text/javascript, */*; q=0.01
```

#### Request Payload Structure (Form URL-Encoded)

The request payload is structured as a nested PHP form-urlencoded array:

| Parameter | Type | Required | Description / Value |
| :--- | :--- | :--- | :--- |
| `action` | `string` | **Yes** | Fixed action identifier: `jet_smart_filters`. |
| `provider` | `string` | **Yes** | Content provider: `jet-engine/todos`. |
| `paged` | `integer` | No | 1-indexed page number (default: `1`). |
| `defaults[post_status][0]` | `string` | **Yes** | `publish`. |
| `defaults[post_type]` | `string` | **Yes** | Custom post type: `imoveis`. |
| `defaults[posts_per_page]` | `string` | **Yes** | Page size: `10`. |
| `defaults[paged]` | `string` | No | Initial page: `1`. |
| `defaults[ignore_sticky_posts]`| `string` | No | `1`. |
| `settings[lisitng_id]` | `string` | **Yes** | Elementor JetEngine listing card template ID: `6919`. |
| `settings[posts_num]` | `integer` | No | Number of posts: `10`. |
| `props[found_posts]` | `integer` | No | Cache/state property indicator. |
| `props[max_num_pages]` | `integer` | No | Max pages indicator. |
| `props[page]` | `integer` | No | Current page indicator. |
| `query[{filter_key}]` | `string` | No | Filter constraints (see Section 3). |

#### Response Format (JSON)

```json
{
  "content": "<div class=\"jet-listing-grid jet-listing\"><div class=\"jet-listing-grid__items ...\">...</div></div>",
  "pagination": {
    "found_posts": 4,
    "max_num_pages": 1,
    "page": 1
  }
}
```

---

## 3. Request Parameters & Filter Behavior

Filters are mapped to taxonomy queries (`_tax_query_*`) and custom post meta queries (`_meta_query_*`):

| Domain Concept | Payload Parameter | Type | Example Values | Backend Logic & Semantics |
| :--- | :--- | :--- | :--- | :--- |
| **Transaction Purpose** | `query[_tax_query_finalidade]` | `string` | `21` (Alugar), `20` (Comprar) | Taxonomy term ID. `21` filters exclusively rental properties. |
| **Property Type** | `query[_tax_query_tipo-de-imovel]`| `string` | `8`, `7`, `34`, `32`, `56`, `50` | Taxonomy term ID (`8` = Apartamento, `7` = Casa, `34` = Loja Comercial, `32` = Casa Geminada, `56` = Chácara, `50` = Cobertura, `55` = Lote). |
| **Municipality / City** | `query[_tax_query_cidade]` | `string` | `24`, `186`, `25` | City taxonomy ID (`24` = Timóteo, `186` = Cel Fabriciano, `25` = Ipatinga). |
| **Neighborhood** | `query[_tax_query_bairro]` | `string` | `35`, `148`, `31` | Neighborhood taxonomy ID (`35` = Funcionários, `148` = Garapa, `31` = Primavera). |
| **Bedrooms** | `query[_meta_query_quartos]` | `string` | `1`, `2`, `3`, `4` | Minimum bedroom count. `4` represents "4 or more". |
| **Bathrooms** | `query[_meta_query_banheiros]`| `string` | `1`, `2`, `3`, `4` | Minimum bathroom count. `4` represents "4 or more". |
| **Price Range** | `query[_meta_query_preco|range]` | `string` | `700_1500`, `1500_3500` | Range formatted as `{min}_{max}` with pipe `|range` suffix. |
| **Reference Code** | `query[_meta_query_codigo-do-imovel]`| `string`| `0473`, `0462` | Exact or partial property reference code. |

---

## 4. Pagination Behavior

- **Page Size**: **10 listings per page** (`defaults[posts_per_page] = 10`).
- **Pagination Parameter**: `paged={page_number}` (1-indexed).
- **Metadata Returned in JSON**:
  - `pagination.found_posts`: Total count of matching listings across all pages.
  - `pagination.max_num_pages`: Total pages available for this query.
  - `pagination.page`: Current page number.
- **Out-of-Bounds Behavior**:
  - Requesting an out-of-bounds page (e.g. `paged=99`) returns HTTP 200 with:
    `{"content": "...<div class=\"jet-listing-not-found\">...</div>", "pagination": {"found_posts": 0, "max_num_pages": 0, "page": 1}}`.
  - The client detects end-of-results when `pagination.found_posts == 0` or `len(cards) == 0`.

---

## 5. Search Results Card Parsing

Search result cards are rendered inside `content` with the CSS class `.jet-listing-grid__item`:

### 5.1 Card Structure & Key Selectors
```html
<div class="jet-listing-grid__item" data-post-id="11217">
  <style>... background-image:url("https://alecorretoramg.com.br/uploads/...jpg"); ...</style>
  <div class="jet-engine-listing-overlay-wrap" data-url="https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/"></div>
  <h2 class="elementor-heading-title">Alugar</h2>
  <h2 class="elementor-heading-title">Cod. 0473</h2>
  <h2 class="elementor-heading-title">Loja Comercial/Quitinete</h2>
  <a class="jet-listing-dynamic-terms__link" href="https://alecorretoramg.com.br/bairro/garapa/">Garapa</a>
  <a class="jet-listing-dynamic-terms__link" href="https://alecorretoramg.com.br/cidade/timoteo/">Timóteo</a>
  <ul class="elementor-icon-list-items">
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text">1</span></li> <!-- Bedrooms -->
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text">1</span></li> <!-- Bathrooms -->
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text"></span></li>  <!-- Parking -->
    <li class="elementor-icon-list-item"><span class="elementor-icon-list-text">50m²</span></li><!-- Area -->
  </ul>
  <div class="jet-listing-dynamic-field__content">R$ 700,00</div>
</div>
```

### 5.2 Field Extraction Matrix
| Field | DOM Selector / Expression | Example Extracted Value |
| :--- | :--- | :--- |
| `property_id` | `card.get('data-post-id')` | `11217` |
| `url` | `card.select_one('.jet-engine-listing-overlay-wrap')['data-url']` | `https://alecorretoramg.com.br/imoveis/loja-comercial-8-2/` |
| `code` | `re.search(r'Cod\.\s*(\d+)', heading.text)` | `0473` |
| `purpose` | First `.elementor-heading-title` (`Alugar`/`Comprar`) | `Alugar` |
| `property_type` | Third or second `.elementor-heading-title` | `Loja Comercial/Quitinete` |
| `neighborhood` | `card.select_one('a[href*="/bairro/"]').text` | `Garapa` |
| `city` | `card.select_one('a[href*="/cidade/"]').text` | `Timóteo` |
| `price_formatted` | `.jet-listing-dynamic-field__content` | `R$ 700,00` |
| `bedrooms` | Icon item index 0 text | `1` |
| `bathrooms` | Icon item index 1 text | `1` |
| `parking_spaces` | Icon item index 2 text | `None` / `1` |
| `area` | Icon item containing `m²` | `50m²` |
| `thumbnail_url` | Regex `background-image:url\(\"([^\"]+)\"\)` from `<style>` | `https://alecorretoramg.com.br/...` |

---

## 6. Property Detail Retrieval

### 6.1 Detail Endpoints
- **Direct ID Endpoint**: `GET https://alecorretoramg.com.br/?p={post_id}`
  - Automatically redirects with HTTP 301 to the canonical SEO URL.
- **Canonical Slug Endpoint**: `GET https://alecorretoramg.com.br/imoveis/{slug}/`
- **Non-Existent ID Handling**: Returns HTTP 404.

### 6.2 Detail Markup Selectors
- **Title**: `h1.elementor-heading-title` (e.g. `Loja Comercial/Quitinete`).
- **Transaction Purpose**: The `.jet-listing-dynamic-terms` field labelled `Finalidade:` supplies its `.jet-listing-dynamic-terms__link` text. Current-property taxonomy takes precedence over title/description keywords; related grids, headers, and footers are ignored. Missing purpose remains an empty string rather than defaulting to sale.
- **Reference Code**: Regex `Código do Imóvel:\s*([A-Za-z0-9_-]+)` from headings (e.g. `0473`).
- **Price**: `.jet-listing-dynamic-field` (e.g. `R$ 700,00`).
- **Description**: `.elementor-widget-text-editor` text.
- **Location**: Extracted from description regex `bairro\s+([^,]+),\s*em\s+([^/]+)/([A-Z]{2})`.
- **Specifications**: `.elementor-icon-list-item` (filtered to exclude headers, footers, and similar properties grid):
  - Bedrooms: regex `Quartos?:\s*(\d+)`
  - Bathrooms: regex `Banheiros?:\s*(\d+)`
  - Parking: regex `(?:Vagas?|Garagem):\s*(\d+)`
  - Area: item containing `Área:` or `m²`
- **Photo Gallery**:
  - Container: `div[data-widget_type="image-carousel.default"]`
  - Photo URLs: `a` tag `href` attributes pointing to full-resolution images (`https://alecorretoramg.com.br/wp-content/uploads/...`).

---

## 7. Supporting Taxonomy Endpoints (REST API)

WordPress REST API endpoints provide taxonomy metadata:

| Taxonomy | Endpoint | Method | Format |
| :--- | :--- | :--- | :--- |
| **Cities** | `GET /wp-json/wp/v2/cidade?per_page=50` | `GET` | JSON Array (`id`, `name`, `slug`, `count`) |
| **Neighborhoods** | `GET /wp-json/wp/v2/bairro?per_page=100` | `GET` | JSON Array (`id`, `name`, `slug`, `count`) |
| **Property Types** | `GET /wp-json/wp/v2/tipo-de-imovel` | `GET` | JSON Array (`id`, `name`, `slug`, `count`) |
| **Transaction Purpose** | `GET /wp-json/wp/v2/finalidade` | `GET` | JSON Array (`id: 21` = Alugar, `id: 20` = Comprar) |
