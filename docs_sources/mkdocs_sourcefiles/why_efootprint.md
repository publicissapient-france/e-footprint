# Why e-footprint ?

For a more in-depth discussion of e-footprint’s genesis by its designer, watch the <a href="https://www.youtube.com/watch?v=pc-H5yySPRo" target="_blank">e-footprint presentation made by Vincent Villet at the 2023 Paris Impact Summit</a> (9 minutes, in French).

## The need for modeling in ecodesign

**We define ecodesign as the process of building or maintaining a digital service while minimizing its environmental impact**. To do so, we first need to understand where its impact comes from and then be able to **anticipate the impact of considered actions to choose the most appropriate one**.

How much intuition can we use to prioritize ecodesign actions ? Is it enough to give tech people a green IT training and let their experience do the rest ? This approach works well for web performance, where the combination of theory and practice allows experienced professionals to build an intuitive understanding of their systems, but there is a major difference between a digital service performance and its environmental impact: a poor performance is perceptible (and even often frustrating !), while the environmental impact lives entirely outside of the reach of our senses. This great distance in space and time between our actions and their impacts (described in more details in this [excellent article from Jean-Marc Jancovici](https://jancovici.com/publications-et-co/contributions-a-ouvrage/une-preface-pour-le-livre-comment-marche-vraiment-le-monde-de-vaclav-smil/)) is a very new and difficult problem for humanity, touches every aspect of modern life, and is especially salient for digital services. **It calls for a fully explicit model because building intuition is simply not possible**.

## How precise does the modeling need to be ?

Now that we know that we need an explicit model, we need to know how precise the model needs to be to allow for good decision-making. Indeed, any understanding is a tradeoff between precision and usability. For example, having in mind a mental model that says "[for an average consumer car, driving at 110km/h on the highway instead of 130km/h reduces the speed by 15% but the oil consumption by 25%](https://scienceetonnante.com/2022/08/07/autoroute-110-au-lieu-de-130/)" is simplistic because many factors influence the result (the exact shape of the car, the wind, the profile of the road etc.). However, I consider it usable for the decision I have to make (which speed to drive at when taking the highway) because I know that the exact oil saving figure for the particular vehicle I’m driving won’t be so far from this simplified average. This example introduces two important concepts that physicists often use:

- **reduced-order modeling**, where the mathematical complexity of a real world phenomenon is voluntarily simplified while preserving enough precision for the task at hand.
- **order of magnitude**, an approximate figure that is easier to obtain and use in reduced-order model computations, and enough to make informed decisions.

**The more complex and variable the studied system is, the more complex (=high order) the corresponding model needs to be before it delivers useful orders of magnitude.**

How complex would a good enough model need to be to effectively guide ecodesign decisions ? It depends on the complexity and variability of digital services. Let’s make some observations and some simple thought experiments to find out the essential parameters.

First and foremost, digital services vary wildly in usage volumes. The biggest social networks have billions of daily visits while your company showcase website might have only a few hundreds. The same ecodesign action leading to a 10% energy consumption reduction will be vastly more impactful on the big system than on the small one, so **usage volume input is critical**.

Then let’s look at the four key components of digital services: **user devices, network, servers and storage**. Different services make use of them in vastly different proportions, making each of them sometimes negligible, sometimes crucial. For example, streaming services make a heavy use of the network, gen AI services use a lot of computing power in servers, and social networks store huge amounts of data. All these different types of objects thus need to be represented in our model.

Lastly, many ecodesign actions involve changing the way users interact with the service, so there needs to be a way to tell the model that users have changed the actions that they typically do. Hence, **user journeys must be part of the model inputs**.

We now have a framework for thinking about the physicality of our digital service: **digital services must at least be described in terms of user journeys ([UserJourney](UserJourney.md)) with their usage information ([UsagePattern](UsagePattern.md)). Each user journey is made of steps ([UserJourneyStep](UserJourneyStep.md)) that make requests ([Job](Job.md)) through a network ([Network](Network.md)) to software ([Service](Service.md)) installed on a server ([Server](Autoscaling.md)), possibly saving data to storage ([Storage](Storage.md)).**

e-footprint was born from the above analysis and the observation that no other tool had taken a modeling approach bringing together all these objects. It started as an Excel modeling and then evolved towards a Python package to allow for greater flexibility in the combination of objects.

Moreover, it is necessary to take a life cycle analysis approach to understand all aspects of environmental impact from cradle to grave. Here the orders of magnitude show that focusing on the fabrication and run phases of the service is a good first approximation, neglecting transport and end of life.

## The difference between the model and the modeling

e-footprint is a modeling tool that embeds a model of the relationships between components of a digital service and the associated environmental footprint. When you describe your digital service with e-footprint, what you get is a modeling of this service.

For more details on the model design decisions in e-footprint, check the [model design deep dive](design_deep_dive.md).

## Get started

Now that you understand the concepts on which e-footprint is built, read the [How to get started](get_started.md) article to start your ecodesign journey !