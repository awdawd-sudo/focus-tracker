import cv2
import mediapipe as mp
import numpy as np
import webbrowser
import time

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DISTRACTION_SECONDS   = 3     # Seconds of looking away before trigger
PITCH_DOWN_THRESHOLD  = 20    # Degrees of downward head tilt
YAW_THRESHOLD         = 60    # Degrees of sideways head turn
COOLDOWN_SECONDS      = 5     # Minimum gap between triggers
MCDONALDS_URL         = "https://www.mcdonalds.com/us/en-us/careers.html"
# ──────────────────────────────────────────────────────────────────────────────

mp_face_mesh = mp.solutions.face_mesh

# 3D reference face model points (standard head shape in mm)
MODEL_POINTS = np.array([
    (0.0,    0.0,    0.0),      # Nose tip        [1]
    (0.0,  -330.0,  -65.0),     # Chin            [152]
    (-225.0, 170.0, -135.0),    # Left eye corner [263]
    (225.0,  170.0, -135.0),    # Right eye corner [33]
    (-150.0,-150.0, -125.0),    # Left mouth      [287]
    (150.0, -150.0, -125.0),    # Right mouth     [57]
], dtype=np.float64)

LANDMARK_IDS = [1, 152, 263, 33, 287, 57]


def get_head_angles(landmarks, frame_shape):
    """Returns (pitch, yaw, roll) in degrees using solvePnP."""
    h, w = frame_shape[:2]

    image_pts = np.array(
        [(landmarks[i].x * w, landmarks[i].y * h) for i in LANDMARK_IDS],
        dtype=np.float64,
    )

    focal = w
    cam_matrix = np.array(
        [[focal, 0, w / 2], [0, focal, h / 2], [0, 0, 1]], dtype=np.float64
    )

    ok, rvec, _ = cv2.solvePnP(
        MODEL_POINTS, image_pts, cam_matrix, np.zeros((4, 1)),
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not ok:
        return None, None, None

    rmat, _ = cv2.Rodrigues(rvec)
    angles, *_ = cv2.RQDecomp3x3(rmat)
    return angles  # pitch, yaw, roll


def check_distraction(pitch, yaw):
    """Returns (is_distracted: bool, reason: str)."""
    if pitch > PITCH_DOWN_THRESHOLD:
        return True, "Looking down at phone"
    if abs(yaw) > YAW_THRESHOLD:
        return True, f"Looking {'left' if yaw > 0 else 'right'}"
    return False, "Focused"


def draw_ui(frame, status, color, bar_pct, busted_count, pitch, yaw):
    h, w = frame.shape[:2]

    cv2.rectangle(frame, (0, 0), (w, 55), (20, 20, 20), -1)

    cv2.putText(frame, status, (12, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2, cv2.LINE_AA)

    if bar_pct > 0:
        bar_w = int(bar_pct * w)
        cv2.rectangle(frame, (0, 55), (bar_w, 63), (0, 60, 255), -1)
        cv2.rectangle(frame, (0, 55), (w, 63), (60, 60, 60), 1)

    debug = f"pitch={pitch:+.1f}  yaw={yaw:+.1f}  busted={busted_count}x"
    cv2.putText(frame, debug, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (140, 140, 140), 1, cv2.LINE_AA)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    busted_count      = 0
    distraction_start = None
    last_trigger      = 0

    print("Focus Tracker running — press Q to quit.\n")

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            frame   = cv2.flip(frame, 1)
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            now     = time.time()

            status  = "No face detected"
            color   = (0, 165, 255)
            bar_pct = 0.0
            pitch = yaw = 0.0

            if results.multi_face_landmarks:
                lm     = results.multi_face_landmarks[0].landmark
                angles = get_head_angles(lm, frame.shape)

                if angles[0] is not None:
                    pitch, yaw, _ = angles
                    distracted, reason = check_distraction(pitch, yaw)

                    if distracted:
                        color = (0, 0, 220)

                        if distraction_start is None:
                            distraction_start = now

                        elapsed   = now - distraction_start
                        bar_pct   = min(elapsed / DISTRACTION_SECONDS, 1.0)
                        remaining = max(DISTRACTION_SECONDS - elapsed, 0)

                        if remaining > 0:
                            status = f"WARNING: {reason}  ({remaining:.1f}s)"
                        else:
                            status = f"BUSTED!  {reason}  — Enjoy flipping burgers 🍔"
                            if now - last_trigger > COOLDOWN_SECONDS:
                                webbrowser.open(MCDONALDS_URL)
                                last_trigger  = now
                                busted_count += 1
                    else:
                        distraction_start = None
                        color  = (0, 210, 0)
                        status = "Focused  ✓"
            else:
                distraction_start = None

            draw_ui(frame, status, color, bar_pct, busted_count, pitch, yaw)
            cv2.imshow("Focus Tracker — stay off your phone!", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Session over. You got busted {busted_count} time(s).")
    if busted_count == 0:
        print("Great focus! 🎉")
    else:
        print("McDonald's is hiring. Just saying. 🍟")


if __name__ == "__main__":
    main()