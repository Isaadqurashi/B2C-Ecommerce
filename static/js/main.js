gsap.registerPlugin(ScrollTrigger);

const marqueeAnimation = () => {
  const sections = document.querySelectorAll(".marquee");
  sections.forEach((section) => {
    const marqueeText = section.querySelector(".marquee-text");
    const w = marqueeText; // Assign marqueeText element to w

    const index = 3; // Define index value (assuming 0, modify as needed)

    const [x, xEnd] = index % 2
      ? ['0%', (w.scrollWidth - section.offsetWidth) * -1]
      : [w.scrollWidth * -1, 0];

    gsap.fromTo(w, { x }, {
      x: xEnd,
      scrollTrigger: {
        trigger: section,
        scrub: 0.5
      }
    });
  });
};


// Define variables
const heroBg = document.querySelector('.hero-bg');
const heroContent = document.querySelector('.hero-content');

// Create parallax effect with ScrollTrigger
gsap.to(heroBg, {
  scrollTrigger: {
    trigger: '.hero',
    start: 'top top',
    end: 'bottom top',
    scrub: true
  },
  y: '50%'
});

gsap.to(heroContent, {
  scrollTrigger: {
    trigger: '.hero',
    start: 'top top',
    end: 'bottom top',
    scrub: true
  },
  y: '10%'
});


  gsap.to(".animate", {
    opacity: 1,
    y: 0,
    duration: 1,
    ease: "power1.out",
    scrollTrigger: {
      trigger: ".animation",
      start: "top 80%",
      end: "bottom 30%",
      toggleActions: "play none none reverse"
    }
  });

const scrollDownBtn = document.querySelector('.scroll-down a');

scrollDownBtn.addEventListener('click', function(e) {
  e.preventDefault();
  
  const targetSection = document.querySelector('#main');
  
  targetSection.scrollIntoView({ behavior: 'smooth' });
});


  marqueeAnimation();


