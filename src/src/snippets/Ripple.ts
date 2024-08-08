// With huge inspiration from https://codepen.io/ainalem/pen/LqvBWO

export function ripple(node: HTMLElement, args: {rippleSize?: number} = {}) {
    const rippleSize = args.rippleSize || 100
    const rippleSizeUnit = "px"

    node.style.position = "relative";
    node.style.overflow = "hidden";

    function click_listener(event: MouseEvent) {
        const rippleElement = document.createElement("div");
        rippleElement.setAttribute("aria-hidden", "true");
        rippleElement.classList.add("ripple");
        const buttonRect = node.getBoundingClientRect();
        rippleElement.style.top = `calc(${event.clientY}px - ${rippleSize/2}${rippleSizeUnit} - ${buttonRect.top}px)`
        rippleElement.style.left = `calc(${event.clientX}px - ${rippleSize/2}${rippleSizeUnit} - ${buttonRect.left}px)`
        rippleElement.style.height = rippleElement.style.width = rippleSize + rippleSizeUnit;
        node.appendChild(rippleElement);
        setTimeout(() => {
            rippleElement.classList.add("material-ripple-active")
        })
    }

    function mouseup() {
        // language=JQuery-CSS
        const queriedRipple = node.querySelector(".ripple:not([data-processed=true])");
        queriedRipple?.setAttribute("data-processed", "true");
        const anim = queriedRipple?.animate([{}, {opacity: 0}], {duration: 700, easing: "ease", iterations: 1});
        anim?.addEventListener("finish", () => {
            queriedRipple?.remove();
        })
    }

    node.addEventListener("mousedown", click_listener)
    node.addEventListener("mouseup", mouseup)
    node.addEventListener("mouseout", mouseup)

    return {
        destroy() {
            node.removeEventListener("mousedown", click_listener)
            node.removeEventListener("mouseup", mouseup)
            node.removeEventListener("mouseout", mouseup)
        },
        update(args: never) {

        }
    }
}