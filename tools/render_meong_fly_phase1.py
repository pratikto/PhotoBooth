"""Deterministic Kivy FBO evidence, not Windows/device acceptance.

Run: python -m tools.render_meong_fly_phase1 --output /tmp/meong-phase1
Fixtures use temporary receipts and never write the user's tutorial marker.
"""
import argparse
import json
import platform
import subprocess
import tempfile
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    from kivy import __version__ as kivy_version
    from kivy.core.window import Window
    from photobooth.meong_fly_gui import MeongFlyStage
    from photobooth.meong_fly_flow import MeongFlyFlow
    from photobooth.meong_fly_receipts import DemoReceiptLedger
    records=[]
    with tempfile.TemporaryDirectory() as tmp:
        for scene,size in ([(s,(450,900)) for s in
                            ('start','scan','game','won','lost','tutorial','layouts')]
                           + [('game',(800,600)),('game',(1200,800))]):
            Window.size=size
            flow=MeongFlyFlow(DemoReceiptLedger(Path(tmp)/'ledger.db'))
            stage=MeongFlyStage(flow,size=size,size_hint=(None,None))
            try:
                flow.screen=scene
                flow.game.y=300
                flow.game.score=10 if scene=='won' else 3
                # Freeze physics only; advance print clock with a controlled pose.
                stage._refresh()
                targets=[('idle',.30),('feed',.96),('hold',1.32),('fall',1.74)] if scene=='start' else [('scene',.96)]
                for label,t in targets:
                    while stage._time + .00001 < t:
                        stage._time=round(stage._time+.03,6)
                        stage._advance_printer(.03)
                    stage._refresh()
                    filename=f'{scene}-{size[0]}x{size[1]}-{label}.png'
                    stage.export_to_png(str(args.output/filename))
                    records.append({'file':filename,'scene':scene,'logical_time':stage._time,
                                    'paper':[vars(p) for p in stage._printer.poses()]})
            finally:
                stage.dispose()
    metadata={'kind':'deterministic Linux Kivy FBO fixtures; NOT Windows acceptance',
              'python':platform.python_version(),'os':platform.platform(),'kivy':kivy_version,
              'sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
              'working_tree':subprocess.check_output(['git','status','--short'],text=True),
              'captures':records}
    (args.output/'capture.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'Captured {len(records)} Kivy frames in {args.output}')


if __name__=='__main__': main()
