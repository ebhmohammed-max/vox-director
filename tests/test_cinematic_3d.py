import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from styles import compose_cinematic_3d_prompt, compose_cinematic_collage_prompt
from clips import cinematic_3d_prompt, cinematic_collage_prompt
import keyframes


class Cinematic3DPromptTests(unittest.TestCase):
    def test_image_prompt_is_cinematic_and_keeps_text_in_post(self):
        prompt = compose_cinematic_3d_prompt(
            "empty underwater water column with natural light shafts",
            aspect="16:9",
            visual_guardrails="no ruins, artifacts, people, or exact location",
        ).lower()
        self.assertIn("physically based render", prompt)
        self.assertIn("volumetric", prompt)
        self.assertIn("no visible text", prompt)
        self.assertIn("no ruins, artifacts, people, or exact location", prompt)
        self.assertNotIn("hand-cut paper", prompt)
        self.assertNotIn("not a 3d render", prompt)

    def test_image_prompt_accepts_shot_specific_look_and_framing(self):
        prompt = compose_cinematic_3d_prompt(
            "unworked bronze patina material study",
            palette="deep umber and subdued copper over teal-black",
            lighting="narrow warm grazing light",
            framing="extreme macro, no complete object silhouette",
        )
        self.assertIn("deep umber and subdued copper", prompt)
        self.assertIn("narrow warm grazing light", prompt)
        self.assertIn("extreme macro", prompt)

    def test_hybrid_collage_prompt_matches_reference_language(self):
        prompt = compose_cinematic_collage_prompt(
            "deep teal underwater light shafts in an anonymous environment",
            visual_guardrails="no ruins, artifacts, or exact location",
        ).lower()
        self.assertIn("paper-collage board", prompt)
        self.assertIn("cinematic, physically based 3d documentary image", prompt)
        self.assertIn("torn cream paper", prompt)
        self.assertIn("red thread", prompt)
        self.assertIn("no legible text", prompt)
        self.assertIn("no ruins, artifacts, or exact location", prompt)

    def test_hybrid_motion_keeps_paper_layers_and_3d_plate_stable(self):
        prompt = cinematic_collage_prompt(
            "parallax",
            element_motion="particles drift only inside the underwater image cut-out",
            visual_guardrails="no archaeological location or artifact",
        ).lower()
        self.assertIn("multi-plane parallax", prompt)
        self.assertIn("paper map/document scraps", prompt)
        self.assertIn("particles drift only inside", prompt)
        self.assertIn("no archaeological location or artifact", prompt)
        self.assertIn("no cuts, resets, melting, morphing", prompt)

    def test_motion_prompt_preserves_scene_and_avoids_collage_language(self):
        prompt = cinematic_3d_prompt(
            "push_in",
            element_motion="suspended silt drifts slowly through the light shafts",
            visual_guardrails="no archaeological features or artifacts",
        ).lower()
        self.assertIn("slow stabilized dolly forward", prompt)
        self.assertIn("suspended silt drifts slowly", prompt)
        self.assertIn("no morphing", prompt)
        self.assertIn("no archaeological features or artifacts", prompt)
        self.assertNotIn("paper cut-out", prompt)
        self.assertNotIn("flat 2d", prompt)

    def test_keyframe_stage_routes_cinematic_style_without_api_calls(self):
        import json
        import tempfile
        from unittest.mock import patch

        class StubProvider:
            def submit_image(self, model, prompt, **params):
                self.prompt = prompt
                self.params = params
                return "stub-job"

        def fake_run_jobs(provider, specs, **kwargs):
            for submit in specs.values():
                submit()
            return {name: None for name in specs}

        for style, marker in (("cinematic_3d", "physically based render"),
                              ("cinematic_collage", "paper-collage board")):
            doc = {
                "style": style,
                "aspect": "16:9",
                "image_resolution": "2k",
                "cinematic_visual_language": {"palette": "teal and navy"},
                "beats": [{
                    "id": "A01",
                    "scene": "empty underwater water column",
                    "framing": "wide view",
                    "visual_guardrails": "no structures or artifacts",
                }],
            }
            stub = StubProvider()
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "beats.json"
                path.write_text(json.dumps(doc))
                with (patch.object(keyframes, "get_provider", return_value=stub),
                      patch.object(keyframes, "run_jobs", side_effect=fake_run_jobs)):
                    keyframes.run(tmp)
                result = json.loads(path.read_text())

            self.assertIn(marker, result["beats"][0]["keyframe_prompt"])
            self.assertIn("no structures or artifacts", result["beats"][0]["keyframe_prompt"])
            self.assertEqual(stub.params["resolution"], "2k")
            self.assertEqual(stub.params["aspect_ratio"], "16:9")


if __name__ == "__main__":
    unittest.main()
