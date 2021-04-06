const SWIPE_LENGTH_THRESHOLD = 50
const SWIPE_MAX_TIME_LENGTH_MS = 400
export class Swipe {
    onLeft;
    onRight;
    onUp;
    onDown;
    constructor(element) {
        this.touchDownPoint = null
        this.movePoints = []
        this.element = element;

        this.element.addEventListener('touchstart', (evt) => {
            this.touchDownPoint = {x: evt.touches[0].clientX, y: evt.touches[0].clientY, time: new Date().getTime()}
        }, false);

        this.element.addEventListener('touchmove', (evt) => {
            this.movePoints.push({x: evt.touches[0].clientX, y: evt.touches[0].clientY, time: new Date().getTime()})
        }, false);

        this.element.addEventListener('touchend', (evt) => {
            this.handleTouchEnd(evt);
        }, false);

    }

    setOnLeft(callback) {
        this.onLeft = callback
    }
    setOnRight(callback) {
        this.onRight = callback
    }
    setOnDown(callback) {
        this.onDown = callback
    }
    setOnUp(callback) {
        this.onUp = callback
    }

    handleTouchEnd(evt) {
        console.log('handleTouchend')
        console.log(evt)
        if (this.touchDownPoint === null ||
            this.movePoints.length === 0 ||
            evt.changedTouches === undefined ||
            evt.changedTouches.length < 1
        ) {
            return
        }
        const lastTouchPoint = {x: evt.changedTouches[0].clientX, y: evt.changedTouches[0].clientY, time: new Date().getTime()}
        const validTouchThresholdTime = (new Date().getTime()) - SWIPE_MAX_TIME_LENGTH_MS
        const validMovePoints = this.movePoints.filter(point => point.time > validTouchThresholdTime)
        if(validMovePoints.length === 0) {
            return
        }

        const xDiff  = -(validMovePoints[0].x - lastTouchPoint.x)
        const yDiff  = validMovePoints[0].y - lastTouchPoint.y
        const swipeLength = Math.sqrt(Math.pow(xDiff, 2) + Math.pow(yDiff, 2))
        const angle = Math.atan2(yDiff, xDiff)
        console.log(`swipeLength: ${swipeLength}, xDiff: ${xDiff}, yDiff: ${yDiff}, angle: ${angle}`)

        if(swipeLength >= SWIPE_LENGTH_THRESHOLD) {
            // With atan2() lower half is between [-0 (right), -1.57 (top), -PI (left)] and upper
            // half is between [0, 1.57 (top), PI (left)]. Note that the sign of PI is not well
            // defined at left, it swings between PI and -PI.
            // We interpret swipes as follows:
            // - angle [PI/4, -PI/4[ : Right swipe.
            // - angle [-PI/4, -3PI/4[: Bottom swipe.
            // - angle [-3PI/4, -PI] and [PI, 3PI/4[ : Left swipe.
            // - angle [3PI/4, PI/4[: Top swipe.
            if(angle <= Math.PI/4 && angle > -Math.PI/4) {
                if(this.onRight !== undefined) {
                    this.onRight()
                    evt.preventDefault()
                }
            } else if(angle <= -Math.PI/4 && angle > -3 * Math.PI / 4) {
                if(this.onDown !== undefined) {
                    this.onDown()
                    evt.preventDefault()
                }
            } else if(angle <= -3 * Math.PI / 4 || (angle <= Math.PI && angle > 3 * Math.PI / 4)) {
                if(this.onLeft !== undefined) {
                    this.onLeft()
                    evt.preventDefault()
                }
            } else if(angle <= 3 * Math.PI && angle > Math.PI/4) {
                if(this.onDown !== undefined) {
                    this.onUp()
                    evt.preventDefault()
                }
            }
        }

        // Reset values.
        this.touchDownPoint = null
        this.movePoints = []
    }
}