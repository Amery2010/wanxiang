import json
import pytest
from wanxiang.errors import WXError
from wanxiang.live_viewer import asset_data, bundle_data, catalog_data


def test_catalogue_summary_matches_full_asset_index():
    catalog = catalog_data()
    assert catalog['parts'] == catalog['assemblies'] == catalog['motions'] == {}
    assert catalog['interfaces'] and catalog['build_context']
    full = bundle_data(thumbnails=False)
    assert len(catalog['assets']) == len(full['assets'])
    fields = ('id', 'name', 'category', 'game_category', 'family', 'level',
              'theme', 'tags', 'runtime', 'game_expansion', 'game_kit',
              'l1', 'l2', 'l3', 'l4')
    for summary, asset in zip(catalog['assets'], full['assets']):
        assert all(summary[field] == asset[field] for field in fields)
        assert summary['report']['triangles'] == asset['report']['triangles']
        assert summary['hero'] == f"/__wanxiang/thumbnails/{asset['id']}.webp"
        assert 'kit' not in summary


@pytest.mark.parametrize('ident', [
    'l1.architecture.game_dungeon.pointed_portal',
    'l3-architecture-building-cottage',
    'l4-interior-living',
])
def test_single_asset_matches_full_definitions_without_unrelated_models(ident):
    full = bundle_data(thumbnails=False)
    payload = asset_data(ident)
    expected = next(asset for asset in full['assets'] if asset['id'] == ident)
    actual = payload['assets'][0]
    assert actual['kit'] == expected['kit']
    assert len(payload['assets']) == 1
    for kind in ('parts', 'assemblies', 'motions'):
        assert len(payload[kind]) < len(full[kind])
        for key, definition in payload[kind].items():
            assert definition == full[kind][key]
    for definition in payload['parts'].values():
        for child in definition.get('shape_params', {}).get('components', []):
            assert child['part'] in payload['parts']
    for definition in payload['assemblies'].values():
        for child in definition.get('instances', []):
            kind = 'parts' if 'part' in child else 'assemblies'
            assert child.get('part', child.get('assembly')) in payload[kind]
    if ident == 'l4-interior-living':
        assert payload['motions']
    assert len(json.dumps(payload)) < len(json.dumps(full))


@pytest.mark.parametrize('ident', ['../registry', 'foo/bar', 'x..y', '', 'not-a-real-model'])
def test_asset_lookup_rejects_unknown_and_unsafe_ids(ident):
    with pytest.raises((ValueError, FileNotFoundError, WXError)):
        asset_data(ident)


def test_single_asset_does_not_read_unrelated_author_definitions(monkeypatch):
    from wanxiang import live_viewer, build_cache
    seen = []
    original = build_cache.read

    def read(path):
        seen.append(str(path))
        return original(path)

    monkeypatch.setattr(build_cache, 'read', read)
    monkeypatch.setattr(live_viewer, 'bundle_data', lambda *_: pytest.fail('full catalogue loaded'))
    payload = asset_data('l3-architecture-building-cottage')
    expected = {
        f'/library/{kind}/{ident}.json'
        for kind in ('parts', 'assemblies', 'motions')
        for ident in payload[kind]
    }
    assert seen
    assert all(any(path.endswith(suffix) for suffix in expected) for path in seen)
